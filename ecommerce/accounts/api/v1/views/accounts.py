from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from ecommerce.accounts.api.v1.serializers.accounts import UserSerializer, ProfilePictureUpdateSerializer
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

    @action(detail=False, methods=['post', ], url_name='change-profile-picture', url_path='change-profile-picture',
            serializer_class=ProfilePictureUpdateSerializer)
    def change_profile_picture(self, request, *args, **kwargs):
        self.parser_classes = [FileUploadParser]
        user = self.request.user
        serializer = self.get_serializer(data=request.data, context={'request': request, 'user': user})
        serializer.is_valid(raise_exception=True)
        profile_picture = self.request.validated_data.get('profile_picture')
        user.profile_picture = profile_picture
        user.save(update_fields=['profile_picture'])
        return Response({
            'profile_picture': user.profile_picture_thumb
        }, status=status.HTTP_201_CREATED)
