from django.db import models

# Create your models here.
from ecommerce.accounts.models import User
from ecommerce.cart.constants import STATUS_CHOICES, PENDING, PAYMENT_CHOICES, KHALTI
from ecommerce.commons.models import UUIDBaseModel
from ecommerce.product.models import Product


class Order(UUIDBaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_carts')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_carts')
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(choices=STATUS_CHOICES, max_length=20, default=PENDING)
    total_price = models.PositiveIntegerField(default=0)
    is_paid = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, null=True, blank=True)

    def __str__(self):
        return f'{self.user.name} --> {self.product.name} --> {self.product.quantity}'


# class Payment(UUIDBaseModel):
#     order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_payments")
#     amount = models.PositiveIntegerField()
#     payment_type = models.CharField(choices=PAYMENT_CHOICES, max_length=15, default=KHALTI)

