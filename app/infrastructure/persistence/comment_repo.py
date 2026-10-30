from sqlalchemy.orm import Session
from app.domain.comment.repository import CommentRepository
from app.domain.comment.entity import Comment
from .models import Comment as CommentModel


class SQLAlchemyCommentRepository(CommentRepository):
    def __init__(self,db: Session):
        self.db=db

    def save(self, comment: Comment)->Comment:
        db_omment=CommentModel(
            content=comment.content,
            article_id=comment.article_id,
            user_id=comment.user_id
            )
        self.db.add(db_omment)
        self.db.commit()
        self.db.refresh(db_omment)
        return Comment(
            id=db_omment.id,
            content=db_omment.content,
            article_id=db_omment.article_id,
            user_id=db_omment.user_id,
            created_at=db_omment.created_at,
            username=db_omment.user_name
        )

    def get_all(self,article_id:int)->list[Comment]:
        comments=self.db.query(CommentModel).filter(CommentModel.article_id==article_id,CommentModel.is_deleted==False).all()
        return [Comment(
            id=comment.id,
            content=comment.content,
            article_id=comment.article_id,
            user_id=comment.user_id,
            created_at=comment.created_at,
            username=comment.user_info.username
            ) for comment in comments]
    
    
