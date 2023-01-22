from django.db import models

# Create your models here.
from ecommerce.accounts.models import User
from ecommerce.cart.models import Order
from ecommerce.commons.models import UUIDBaseModel


class ShippingDetail(UUIDBaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_shipping_detail')
    email = models.EmailField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=14, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    postal_code = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.name}-->{self.address}'


class ShippingOrder(UUIDBaseModel):
    shipping_detail = models.ForeignKey(ShippingDetail, on_delete=models.CASCADE,
                                        related_name='shipping_detail_shipping_order')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_shipping_detail')

    def __str__(self):
        return f'{self.shipping_detail.__str__()}-->{self.order.__str__()}'
