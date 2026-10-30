from app.domain.comment.repository import CommentRepository
from app.domain.article.repository import ArticleRepository
from app.domain.user.repository import UserRepository
from app.domain.comment.entity import Comment

class CommentService:
    def __init__(
            self,
            comment_repo:CommentRepository,
            article_repo:ArticleRepository,
            user_repo:UserRepository
            ):
        self.comment_repo=comment_repo  #只依赖接口
        self.article_repo=article_repo
        self.user_repo=user_repo

    def create_comment(self,content: str,article_id: int,user_id: int)->Comment:
        if not self.article_repo.get_by_id(article_id):
            raise ValueError("文章不存在")
        if not self.user_repo.get_by_id(user_id):
            raise ValueError("用户不存在")
        
        comment=Comment(
            id=None,
            content=content,
            article_id=article_id,
            user_id=user_id
            )
        #交给接口去保存
        return self.comment_repo.save(comment)

    def list_comment(self)->list[Comment]:
        comments=self.comment_repo.list_all()
        return comments