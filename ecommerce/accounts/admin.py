from django.contrib import admin

# Register your models here.
from ecommerce.accounts.models import User

admin.site.register(User)
