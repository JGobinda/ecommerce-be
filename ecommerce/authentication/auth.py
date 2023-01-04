from cuser.middleware import CuserMiddleware
from django.utils import timezone
from knox.auth import TokenAuthentication as KnoxTokenAuthentication

from .models import KnoxAuthToken


class CustomKnoxTokenAuthentication(KnoxTokenAuthentication):
    model = KnoxAuthToken

    def authenticate_credentials(self, key):
        user, token = super().authenticate_credentials(key)
        token_obj = self.model.objects.get(authtoken_ptr=token)
        token_obj.last_used = user.last_activity = timezone.now()
        token_obj.save(update_fields=['last_used'])
        user.save(update_fields=['last_activity'])
        CuserMiddleware.set_user(user)
        return user, token
