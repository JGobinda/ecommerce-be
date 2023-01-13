from django.contrib import admin

# Register your models here.
from ecommerce.shipping.models import ShippingDetail, ShippingOrder

admin.site.register([ShippingDetail, ShippingOrder])
