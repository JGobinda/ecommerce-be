import random

from django_q.tasks import async_task

# from config import settings
from config.settings import HOST_EMAIL
# from ecommerce.cart.constants import KHALTI


def send_order_placed_mail(user, shipping_mail=""):
    recipients = [user.email]
    if shipping_mail:
        recipients = recipients.append(shipping_mail)
    subject = f"Hello {user.name},\n Your payment method has been successfully saved\n Your order is in process!"
    async_task(
        'django.core.mail.send_mail',
        "Payment Method Saved",
        subject,
        HOST_EMAIL,
        [recipients],
        fail_silently=True
    )
    return True


def send_payment_completed_mail(user, shipping_mail=""):
    recipients = [user.email]
    if shipping_mail:
        recipients = recipients.append(shipping_mail)
    async_task(
        'django.core.mail.send_mail',
        "Payment Successful",
        f"Hello {user.name},\n Your payment has been successful, Your requested products will be delivered soon.\n "
        f"Thanks for choosing us. Your product is on the way",
        HOST_EMAIL,
        recipients,
        fail_silently=True
    )
    return True
