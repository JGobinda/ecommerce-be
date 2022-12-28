from django.urls import include, path

urlpatterns = [
    # path('accounts/', include('ecommerce.accounts.api.v1.urls')),
    path('commons/', include('ecommerce.commons.api.v1.urls')),
    # path('contact/')
]
