from app.domain.notification.service import NotificationService
from app.infrastructure.tasks.email_tasks import send_notification_email_task


class CeleryNotificationServiceImpl(NotificationService):
   
   def send_new_article_email(self, author_email: str, article_title: str)->None:
        
        send_notification_email_task.delay(author_email,article_title)