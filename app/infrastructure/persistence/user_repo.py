from sqlalchemy.orm import Session
from app.domain.user.repository import UserRepository
from app.domain.user.entity import User
from .models import User as UserModel

class SQLAlchemyUserRepository(UserRepository):
    def __init__(self,db: Session):
        self.db=db

    def save(self, user: User)->User:
        db_user=UserModel(
            username=user.username,
            password=user.password_hash
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return User(
            id=db_user.id,
            username=db_user.username,
            password_hash=db_user.password
        )
    def get_by_id(self, user_id: int) -> User | None:
        # 用 SQLAlchemy 根据 id 查询
        model = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not model:
            return None
        return User(id=model.id, username=model.username, password_hash=model.password)

    def get_by_username(self, username: str)->User | None:
        model=self.db.query(UserModel).filter(UserModel.username==username,UserModel.is_deleted==False).first()
        if not model:return None
        return User(id=model.id,username=model.username,password_hash=model.password)