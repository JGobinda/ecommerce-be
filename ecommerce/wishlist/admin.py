from django.contrib import admin

# Register your models here.
from ecommerce.wishlist.models import WishList

admin.site.register([WishList])
