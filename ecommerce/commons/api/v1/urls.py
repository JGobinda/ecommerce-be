from rest_framework.routers import DefaultRouter
from .views.file_upload import FileViewSet
ROUTER = DefaultRouter()

ROUTER.register('file', FileViewSet, basename='course')

urlpatterns = [

] + ROUTER.urls
