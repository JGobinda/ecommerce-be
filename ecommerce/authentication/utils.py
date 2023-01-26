import random

from django_q.tasks import async_task

from config import settings
from config.settings import HOST_EMAIL
from ecommerce.authentication.models import UserOTPVerification


def user_account_activation_otp_to_email(user):
    otp = settings.DEFAULT_OTP
    if not settings.OTP_TEST_MODE:
        import random
        otp = random.randrange(100000, 999999)

    otp_request = UserOTPVerification.objects.create(email=user.email, otp=otp)
    async_task(
        'django.core.mail.send_mail',
        "User Registration OTP!!!",
        f"Hello user, the otp for user registration is {otp}. OTP expires in a day.",
        HOST_EMAIL,
        [user.email],
        fail_silently=True
    )
    return otp_request


def send_password_reset_email(user):
    otp = settings.DEFAULT_OTP
    if not settings.OTP_TEST_MODE:
        otp = random.randrange(100000, 999999)

    otp_request = UserOTPVerification.objects.create(email=user.email, otp=otp)
    async_task(
        'django.core.mail.send_mail',
        "Password reset",
        f"Hello user, the otp for account password reset is {otp}. OTP expires in a day.",
        HOST_EMAIL,
        [user.email],
        fail_silently=True
    )
    return otp_request
