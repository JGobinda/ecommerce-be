from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.response import Response
from ecommerce.commons.mixins.viewsets import CreateViewSetMixin
from ..serializers.registration import UserAccountRegistrationSerializer
UserModel = get_user_model()


class UserAccountRegistrationView(CreateViewSetMixin):
    """
        create: Register user as Student

        activate: Activate a user
    """

    serializer_class = UserAccountRegistrationSerializer
    permission_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = request.data.get('email')
        user = UserModel.objects.filter(email=email)
        if user and not user[0].is_active:
            user.update(first_name=request.data.get('first_name'), middle_name=request.data.get('middle_name'),
                        last_name=request.data.get('last_name'), name=request.data.get('name'), phone_number=
                        request.data.get('phone_number'))
            user_instance = user[0]
            user_instance.set_password(request.data.get('password'))
            user_instance.save()
            headers = self.get_success_headers(serializer.data)
            return Response({"detail": "An activation code has been sent to you"},
                            status=status.HTTP_200_OK,
                            headers=headers)
        elif user and user[0].is_active:
            return Response({
                "detail": "User is already active!",
                "code": "AUTHED"
            })
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({"detail": "An activation code has been sent to you "}, status=status.HTTP_201_CREATED,
                        headers=headers)

