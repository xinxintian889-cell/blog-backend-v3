from abc import ABC,abstractmethod

class NotificationService(ABC):
    """通知服务接口： 只定义要干什么，不管怎么干"""

    @abstractmethod
    def send_new_article_email(self,author_email: str,article_title: str)->None:
        pass
