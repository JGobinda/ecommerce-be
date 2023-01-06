from django.db import models

# Create your models here.
from ecommerce.accounts.models import User
from ecommerce.cart.constants import STATUS_CHOICES, PENDING
from ecommerce.commons.models import UUIDBaseModel
from ecommerce.product.models import Product


class Order(UUIDBaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_carts')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_carts')
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(choices=STATUS_CHOICES, max_length=20, default=PENDING)

    def __str__(self):
        return f'{self.user.name} --> {self.product.name} --> {self.product.quantity}'
