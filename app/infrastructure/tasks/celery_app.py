from celery import Celery
from app.config import settings

redis_url=settings.REDIS_URL

celery_app=Celery(
    "blog_worker",
    broker=redis_url,   #消息队列（用来存任务）
    backend=redis_url,  #结果存储（用来存任务执行结果）
    include=["app.infrastructure.tasks.email_tasks"]  #告诉celery去哪里找任务
)

#配置时区等参数
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/shanghai",
    enable_urc=True

)