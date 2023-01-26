from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from ecommerce.accounts.api.v1.serializers.accounts import UserSerializer, ProfilePictureUpdateSerializer, \
    PasswordChangeSerializer
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

    @action(detail=True, methods=['post'], url_path='password', url_name='password',
            serializer_class=PasswordChangeSerializer)
    def password(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.serializer_class(data={
            'user': user.id,
            'old_password': request.data.get('old_password'),
            'password': request.data.get('password'),
            'repeat_password': request.data.get('repeat_password'),
            'logout_from_other_devices': request.data.get('logout_from_other_devices')
        }, context={'request': request, 'user': user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Password has been updated successfully'})
