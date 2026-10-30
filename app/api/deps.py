
#依赖注入装配器
from fastapi import Depends,HTTPException,Request
from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer
from jose import jwt,JWTError
from app.config import settings
from app.infrastructure.security.jwt import ALGORITHM
from sqlalchemy.orm import Session
from app.infrastructure.persistence.database import get_master_db,get_slave_db
from typing import Annotated
import redis
import time
from app.infrastructure.persistence.redis_client import get_redis


#导入接口和实现
from app.domain.article.repository import ArticleRepository
from app.infrastructure.persistence.article_repo import SQLAlchemyArticleRepository
from app.application.services.article_service import ArticleService

from app.domain.user.repository import UserRepository
from app.infrastructure.persistence.user_repo import SQLAlchemyUserRepository
from app.application.services.user_service import UserService

from app.domain.comment.repository import CommentRepository
from app.infrastructure.persistence.comment_repo import SQLAlchemyCommentRepository
from app.application.services.comment_service import CommentService

from app.infrastructure.security.hasher import PasswordHasher
from app.infrastructure.security.jwt import JWTProvider

#通知服务
from app.domain.notification.service import NotificationService
from app.infrastructure.notification.celery_notification_impl import CeleryNotificationServiceImpl


#--------应该根据业务语义（Bounded Context/Service 的职责）来划分,非只看post/get------

def get_article_write_repo(db: Session=Depends(get_master_db))->ArticleRepository:
    repo=SQLAlchemyArticleRepository(db)
    return repo
#新增通知服务的装配
def get_notification_service()->NotificationService:
    return CeleryNotificationServiceImpl()

#---article---
#所有写操作（注册、发文章、写评论）的依赖注入，传MasterSession
def get_article_write_service(
        repo: Annotated[ArticleRepository,Depends(get_article_write_repo)],
        notifier: Annotated[NotificationService,Depends(get_notification_service)],
        r:  Annotated[redis.Redis,Depends(get_redis)]
)->ArticleService:
    return ArticleService(repo,cache=r,notifier=notifier)

#所有读操作（查文章列表、查详情）的依赖注入，传SlaveSession
def get_article_read_service(
        db: Annotated[Session,Depends(get_slave_db)],
        r:  Annotated[redis.Redis,Depends(get_redis)]
)->ArticleService:
    repo=SQLAlchemyArticleRepository(db)
    return ArticleService(repo,cache=r)


#---user---
def get_user_write_service(
        db: Annotated[Session,Depends(get_master_db)],
        r:  Annotated[redis.Redis,Depends(get_redis)]
)->UserService:
    hasher=PasswordHasher()
    token_provider=JWTProvider()
    repo=SQLAlchemyUserRepository(db)
    return UserService(repo,cache=r,hasher=hasher,token_provider=token_provider)

def get_user_read_service(
        db: Annotated[Session,Depends(get_slave_db)],
        r:  Annotated[redis.Redis,Depends(get_redis)]
)->UserService:
    repo=SQLAlchemyUserRepository(db)
    return UserService(repo,cache=r)

#---comment---
def get_comment_write_service(
        db: Annotated[Session,Depends(get_master_db)],
        r:  Annotated[redis.Redis,Depends(get_redis)]
)->CommentService:
    repo=SQLAlchemyCommentRepository(db)
    return CommentService(repo,cache=r)

def get_comment_read_service(
        db: Annotated[Session,Depends(get_slave_db)],
        r:  Annotated[redis.Redis,Depends(get_redis)]
)->CommentService:
    repo=SQLAlchemyCommentRepository(db)
    return CommentService(repo,cache=r)


security=HTTPBearer()

def get_current_user_id(
        credentials:Annotated[HTTPAuthorizationCredentials,Depends(security)],
        r=Depends(get_redis)
        )->int:
    """保安: 校验Token是否合法，并返回用户ID"""
    token=credentials.credentials
    #鉴权校验中拦截黑名单token
    #1.先查黑名单
    if r.exists(f"jwt_blacklist:{token}"):
        raise HTTPException(status_code=401,detail="Token 已失效，请重新登录")
        
    try:
        payload=jwt.decode(token,settings.JWT_SECRET_KEY,algorithms=[ALGORITHM])
        user_id=int(payload.get("sub"))
        return user_id
    except JWTError:
        raise HTTPException(status_code=401,detail="Token 无效或已过期")

#基于redis的接口限流（固定窗口计数器）
#限流依赖
def rate_limit(max_requests: int,window_seconds: int):
    """限流工厂：每分钟最多请求max_requests 次"""
    def dependency(
            request: Request,
            r = Depends(get_redis)
            ):
        #以客户端IP 和请求路径作为限流key
        client_ip=request.client.host
        path= request.url.path
        key= f"rate_limit:{client_ip}:{path}"

        #获取当前请求次数
        current=r.get(key)
        if current and int(current) >= max_requests:
            raise HTTPException(status_code=429,detail="请求过于频繁，请稍后再试！")

        #自增并设置过期时间（第一次请求时设置）
        r.incr(key)
        if not current:
            r.expire(key,window_seconds)
    return dependency
