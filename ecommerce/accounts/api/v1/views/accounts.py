from rest_framework.viewsets import ModelViewSet

from ecommerce.accounts.api.v1.serializers.accounts import UserSerializer
from ecommerce.accounts.models import User


class UserViewSet(ModelViewSet):
    lookup_field = 'uuid'
    lookup_url_kwarg = 'uuid'
    serializer_class = UserSerializer
    queryset = User.objects.all()
