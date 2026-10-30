from app.domain.user.repository import UserRepository
from app.domain.user.entity import User
from fastapi import HTTPException

class UserService:
    #依赖注入
    def __init__(self,repo:UserRepository,cache,hasher,token_provider):
        self.repo=repo  #只依赖接口
        self.hasher=hasher
        self.token_provider=token_provider

    def register(self,username: str,password= str)->User:
        if self.repo.get_by_username(username):
            raise HTTPException(status_code=400,detail="用戶名已存在")

        #使用注入进来的工具加密
        hashed_pwd=self.hasher.hash(password)
        user=User(
            id=None,
            username=username,
            password_hash=hashed_pwd
            )
        #交给接口去保存
        return self.repo.save(user)

    def login(self,username:str,password:str)->dict:
        user=self.repo.get_by_username(username)
        if not user:
            raise HTTPException(status_code=400,detail="用户名或密码错误")

        #调用纯业务方法验证密码
        if not user.verify_password(password,self.hasher):
            raise HTTPException(status_code=400,detail="用户名或密码错误")

        #生成token并返回
        token=self.token_provider.create_token(user.id)
        return {"access_token":token,"token_type":"bearer"}


