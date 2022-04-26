import threading
from account.models import UserAccount
import random
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone


class EmailSender(threading.Thread):
    def __init__(self, user_email):
        self.user_email = user_email
        threading.Thread.__init__(self)

    def run(self):
        user = UserAccount.objects.all().filter(
            email=self.user_email).first()
        token = random.randint(100000, 999999)
        subject = "Forgot password verification"
        message = f'Hello! \n Use this verification code to reset your password: {token} \nRegards,\n Muse.'
        email_from = settings.EMAIL_HOST_USER
        recepient_list = [self.user_email]
        send_mail(subject, message, email_from, recepient_list)
        user.password_reset_token = token
        user.password_reset_token_expiration = timezone.now() + timezone.timedelta(minutes=5)
        user.save()
