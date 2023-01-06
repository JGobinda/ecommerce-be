from django.contrib import admin

# Register your models here.
from ecommerce.cart.models import Order

admin.site.register(Order)
