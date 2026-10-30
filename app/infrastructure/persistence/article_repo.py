from sqlalchemy.orm import Session
from app.domain.article.repository import ArticleRepository
from app.domain.article.entity import Article
from .models import Article as ArticleModel

class SQLAlchemyArticleRepository(ArticleRepository):
    def __init__(self,db: Session):
        self.db=db

    def save(self, article: Article)->Article:
        db_article= ArticleModel(
            title=article.title,
            content=article.content,
            author_id=article.author_id
        )
        self.db.add(db_article)
        self.db.commit()
        self.db.refresh(db_article)

        return Article(
            id=db_article.id,
            title=db_article.title,
            content=db_article.content,
            author_id=db_article.author_id,
            author_name=db_article.author_info.username,
            created_at=db_article.created_at
        )

    def get_by_title(self, title:str)->Article | None:
        model=self.db.query(ArticleModel).filter(ArticleModel.title==title,ArticleModel.is_deleted==False).first()
        if not model:return None
        return Article(
            id=model.id,
            title=model.title,
            content=model.content,
            author_id=model.author_id,
            created_at=model.created_at
        )
    def get_by_id(self, article_id:int)->Article | None:
        model=self.db.query(ArticleModel).filter(ArticleModel.id==article_id,ArticleModel.is_deleted==False).first()
        if not model:return None
        return Article(
            id=model.id,
            title=model.title,
            content=model.content,
            author_id=model.author_id,
            created_at=model.created_at
        ) 
    def list_all(self)->list[Article]:
        articles=self.db.query(ArticleModel).order_by(ArticleModel.created_at.desc(),ArticleModel.is_deleted==False).all()
        return [Article(
            id=model.id,
            title=model.title,
            content=model.content,
            author_id=model.author_id,
            created_at=model.created_at
        ) for model in articles]