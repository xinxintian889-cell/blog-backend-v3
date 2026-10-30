#抽象接口
from abc import ABC,abstractmethod
from .entity import Comment

class CommentRepository(ABC):
    @abstractmethod
    def save(self,comment:Comment)->Comment:
        pass

    @abstractmethod
    def list_all(self)->list[Comment]:
        pass