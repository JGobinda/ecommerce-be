from django.urls import include, path

urlpatterns = [
    path('accounts/', include('ecommerce.authentication.api.v1.urls')),
    path('commons/', include('ecommerce.commons.api.v1.urls')),
    path('contact/', include('ecommerce.contact.api.v1.urls'))
]
