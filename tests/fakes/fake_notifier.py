from app.domain.notification.service import NotificationService

class FakeNotificationService(NotificationService):
    def __init__(self):
        self.sent_emails=[] #记录下来方便测试断言

    def send_new_article_email(self, author_email, article_title)->None:
        self.sent_emails.append((author_email,article_title))