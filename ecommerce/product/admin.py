from django.contrib import admin

# Register your models here.
from ecommerce.product.models import Product, ProductImage, Category, ProductFeature

admin.site.register([Product, ProductImage, Category, ProductFeature])
