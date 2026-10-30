import time
import logging
from .celery_app import celery_app

logger=logging.getLogger(__name__)

@celery_app.task(bind=True,max_retries=3)
def send_notification_email_task(self,user_email: str,article_title: str):
    """
    发送通知邮件的异步任务
    bind=True 允许我们访问self（用于重试）
    max_retries=3 失败最多重试3次
    """
    try:
        logger.info(f"开始给{user_email}发送关于《{article_title}》的邮箱...")

        #模拟发邮件极其耗时的过程（真实场景这里调用 smtplib 或第三方 API）
        time.sleep(5)
        logger.info(f"给{user_email}的邮件发送成功！")
        return f"Email sent to {user_email}"

    except Exception as exc:
        logger.error(f"发送邮件失败，准备重试：{exc}")

        #如果失败，等待10秒后重试
        raise self.retry(exc=exc,countdown=10)