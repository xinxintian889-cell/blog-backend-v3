from app.domain.article.repository import ArticleRepository
from app.domain.article.entity import Article
from datetime import datetime

#假仓库，就是把数据库这个仓库的方法重写，代替链接
class FakeArticleRepository(ArticleRepository):
    def __init__(self):
        # 用一个字典假装是数据库表
        self.db = {}
        self.next_id = 1

    def save(self, article: Article) -> Article:
        # 模拟存入数据库，分配 ID
        actual_author_id =article.author_id["id"] if isinstance(article.author_id,dict) else article.author_id
        fake_article=Article(
            id = self.next_id,
            title=article.title,
            content=article.content,
            author_id=actual_author_id, 
            created_at=datetime.now()
        )
        self.db[self.next_id] = fake_article 
        self.next_id += 1            # 为下一篇文章准备 ID

        return fake_article

    def get_by_id(self, article_id: int) -> Article | None:
        return self.db.get(article_id)

    def get_by_title(self, title: str) -> Article | None:
        for article in self.db.values():
            if article.title == title:
                return article
        return None

    def list_all(self) -> list[Article]:
        return list(self.db.values())