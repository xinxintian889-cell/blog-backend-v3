from fastapi.testclient import TestClient
from main import app
from app.api.deps import get_article_write_service,get_article_read_service
from app.application.services.article_service import ArticleService
from tests.fakes.fake_article_repo import FakeArticleRepository
from app.api.routers.article import get_current_user_id
from tests.fakes.fake_cache import FakeCache
from tests.fakes.fake_notifier import FakeNotificationService

#这里是当做一个介质来将假仓库和真数据库做替代，这一个动作

# 准备一个全局的假仓库，让接口测试使用
fake_repo = FakeArticleRepository()
fake_cache=FakeCache()
fake_notifier=FakeNotificationService()
def override_get_article_write_service():
    return ArticleService(repo=fake_repo,cache=fake_cache,notifier=fake_notifier)

def override_get_article_read_service():
    return ArticleService(repo=fake_repo,cache=fake_cache,notifier=fake_notifier)

# 核心魔法：把 FastAPI 里默认的连接数据库的依赖，替换掉！
app.dependency_overrides[get_article_write_service] = override_get_article_write_service
app.dependency_overrides[get_article_read_service] = override_get_article_read_service

# 1. 伪造一个用户对象，或者直接返回 True
def override_get_current_user_id():
    return {"id": 1, "username": "test_user"} # 或者你系统里的 User 模型对象

# 2. 覆盖认证依赖
app.dependency_overrides[get_current_user_id] = override_get_current_user_id # 注意替换 get_current_user 为你真实的函数名


client = TestClient(app)

def test_create_article_api():
    response = client.post("/articles/", json={
        "title": "接口测试",
        "content": "通过 HTTP 层测试",
        "author_id": 1
    })
    print("\nResponse JSON:",response.json())
    assert response.status_code == 200
    assert response.json()["title"] == "接口测试"

