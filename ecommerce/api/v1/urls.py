from django.urls import include, path

urlpatterns = [
    path('accounts/', include('ecommerce.authentication.api.v1.urls')),
    path('commons/', include('ecommerce.commons.api.v1.urls')),
    path('contact/', include('ecommerce.contact.api.v1.urls')),
    path('product/', include('ecommerce.product.api.v1.urls')),
    path('wishlist/', include('ecommerce.wishlist.api.v1.urls')),
    path('order/', include('ecommerce.cart.api.v1.urls')),
    path('user/', include('ecommerce.accounts.api.v1.urls'))
]
