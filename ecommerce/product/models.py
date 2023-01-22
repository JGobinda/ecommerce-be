from django.db import models

# Create your models here.
from ecommerce.accounts.models import User
from ecommerce.commons.models import UUIDBaseModel, FileUpload


class Category(UUIDBaseModel):
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title


class Product(UUIDBaseModel):
    name = models.CharField(max_length=500, null=True, blank=True)
    manufacturer = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField()
    category = models.ManyToManyField(Category, related_name='category_products')
    in_stock = models.BooleanField(default=True)
    code = models.CharField(max_length=10, null=True, blank=True)
    base_price = models.PositiveIntegerField(default=0)
    discount_price = models.PositiveIntegerField(default=0)
    quantity = models.PositiveIntegerField(default=0)
    sold_quantity = models.PositiveIntegerField(default=0)
    total_ratings = models.PositiveIntegerField(default=0)
    featured = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class ProductImage(UUIDBaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_product_images')
    image = models.ForeignKey(FileUpload, on_delete=models.CASCADE, related_name='file_product_images')

    def __str__(self):
        return self.product.name


class ProductFeature(UUIDBaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_product_features')
    title = models.CharField(max_length=1000, default='')

    def __str__(self):
        return self.title


class ProductRating(UUIDBaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_product_ratings')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_product_ratings')
    ratings = models.PositiveIntegerField(default=1)