from rest_framework.viewsets import ModelViewSet

from ecommerce.accounts.api.v1.serializers.accounts import UserSerializer
from ecommerce.accounts.models import User


class UserViewSet(ModelViewSet):
    lookup_field = 'username'
    lookup_url_kwarg = 'username'
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_object(self):
        if self.kwargs['username'] == 'me':
            self.kwargs['username'] = self.request.user.username
        return super().get_object()
