from django.conf import settings
from django.contrib.auth import login
from django.utils import timezone
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.settings import api_settings

from ..serializers.token import CustomAuthTokenSerializer
from ....models import KnoxAuthToken
from ....auth import CustomKnoxTokenAuthentication


class ObtainAuthTokenView(ObtainAuthToken):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    authentication_classes = [CustomKnoxTokenAuthentication]

    def post(self, request, *args, **kwargs):
        serializer = CustomAuthTokenSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        # Adding user_agent and app specific information in AuthToken Model
        detail = dict(
            # user_agent=request.user_agent.ua_string,
            device_id=request.headers.get(settings.APP_HEADER_INFORMATION.get('DEVICE_UNIQUE_ID')),
            app_version=request.headers.get(settings.APP_HEADER_INFORMATION.get('APP_VERSION')),
        )
        instance, token = KnoxAuthToken.objects.create(detail=detail, user=user)

        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        groups = user.groups.all()
        if groups:
            grp = groups.first().name
        else:
            grp = None
        login(request, user)
        return Response(
            {
                'token': token,
                'available_tokens': KnoxAuthToken.objects.filter(user=user).count(),
                'group': grp,
                'username': user.username
            }
        )
