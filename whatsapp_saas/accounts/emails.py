from django.core.mail import send_mail
from django.conf import settings
import random
from .models import User
from django.utils import timezone

def send_otp_via_email(email):
    subject = 'Your OTP Code'
    otp = random.randint(1000, 9999)
    message = f'Your OTP code is {otp}'
    email_from = settings.EMAIL_HOST
    send_mail(subject, message, email_from, [email])
    user_obj = User.objects.get(email=email)
    user_obj.otp = otp
    user_obj.otp_created_at = timezone.now()  
    user_obj.save()
