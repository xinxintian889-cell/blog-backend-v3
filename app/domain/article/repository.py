#抽象接口
from abc import ABC,abstractmethod
from .entity import Article

class ArticleRepository(ABC):
    @abstractmethod
    def save(self,article:Article)->Article:
        pass

    @abstractmethod
    def get_by_id(self,article_id:int)->Article | None:
        pass

    @abstractmethod
    def get_by_title(self,title:str)->Article | None:
        pass

    @abstractmethod
    def list_all(self)->list[Article]:
        pass