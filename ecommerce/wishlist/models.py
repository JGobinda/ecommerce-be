from django.db import models


# Create your models here.
from ecommerce.accounts.models import User
from ecommerce.commons.models import UUIDBaseModel
from ecommerce.product.models import Product


class WishList(UUIDBaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_wishlists')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='user_products')

    def __str__(self):
        return f'{self.product.name} + "-->" + {self.user.name}'
