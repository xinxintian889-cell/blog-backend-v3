import json
import time

from app.domain.article.repository import ArticleRepository
from app.domain.article.entity import Article
from app.domain.exceptions import DuplicateTitleError,ArticleNotFoundError,IsnullTitleError
from app.infrastructure.cache.redis_lock import RedisLock
from app.domain.notification.service import NotificationService

class ArticleService:
    def __init__(
            self,
            repo:ArticleRepository,
            cache,
            notifier: NotificationService
            ):
        self.repo=repo  #只依赖接口
        self.cache=cache
        self.notifier=notifier

    def incr_views(self, article_id: int):
        # 不查数据库，直接在 Redis 里原子自增
        self.cache.incr(f"article:views:{article_id}")
        
    def create_article(self,title: str,content: str,author_id: int)->Article:
        if not title or not title.strip():  #需要考虑title字段被少传 和title为空 两种情况
            raise IsnullTitleError("文章标题不能为空")
        if self.repo.get_by_title(title):
            raise DuplicateTitleError("文章标题已存在")
        
        article=Article(
            id=None,
            title=title,
            content=content,
            author_id=author_id
            )
        #交给接口去保存
        save_article=self.repo.save(article)
        self.cache.delete("article_list_page_1")

        #直接调用通知接口（底层不知是celery）
        #真实场景需要从UserRepository 查出来
        self.notifier.send_new_article_email("author@test.com",article.title)
        
        return save_article

    def get_article(self,article_id: int)->Article:
        # article=self.repo.get_by_id(article_id)
        # if not article:
        #     raise ArticleNotFoundError("文章不存在")
        # return article

        #------分布式锁逻辑------

        cache_key=f"article:{article_id}"
        lock_key=f"lock:article:{article_id}"

        #用while True 代替递归
        while True:
            #1.先查缓存
            cache_data=self.cache.get(cache_key)
            if cache_data:
                return Article(**json.loads(cache_data))
            
            #2.缓存没命中，尝试获取分布式锁
            lock=RedisLock(self.cache)
            identifier=lock.acquire(lock_key)
            if identifier:
                #3.抢到锁，再次检查缓存（防止获取锁的间隙，别人已经重建了缓存）
                try:
                    cache_data=self.cache.get(cache_key)
                    if cache_data:
                        return Article(**json.loads(cache_data))

                    #查库并回写
                    article=self.repo.get_by_id(article_id)
                    if not article:
                        raise ArticleNotFoundError("文章不存在")

                    #写入缓存（设置5 分钟过期）
                    self.cache.setex(cache_key,300,json.dumps(article.__dict__))
                    return article
                finally:
                    #释放锁防止死锁
                    lock.release(lock_key,identifier)
            else:
                #没拿到锁的请求，不是去递归，等一会儿，然后通过continue 再次进入循环查缓存
                time.sleep(0.2)
                continue    #跳出本轮if，进入下一次while循环
        
        
        #----下面递归方法容易导致栈溢出
        # if cache_data:
        #     return Article(**json.loads(cache_data))

        # #缓存没命中，尝试获取分布式锁
        # lock=RedisLock(self.cache)
        # lock_key=f"lock:article:{article_id}"
        # identifier=lock.acquire(lock_key)
        # if identifier:
        #     try:
        #         #获取到锁，再次检查缓存（防止获取锁的间隙，别人已经重建了缓存）
        #         cache_data=self.cache.get(cache_key)
        #         if cache_data:
        #             return Article(**json.loads(cache_data))

        #         #查数据库
        #         article=self.repo.get_by_id(article_id)
        #         if not article:
        #             raise ArticleNotFoundError("文章不存在")

        #         #写入缓存（设置5 分钟过期）
        #         self.cache.setex(cache_key,300,json.dumps(article.__dict__))
        #         return article
        #     finally:
        #         #释放锁防止死锁
        #         self.lock.release(lock_key,identifier)
        # else:
        #     #没拿到锁的请求，自旋等待一会儿，然后递归调用自己重新查缓存
        #     time.sleep(0.5)
        #     return self.get_article(article_id)

