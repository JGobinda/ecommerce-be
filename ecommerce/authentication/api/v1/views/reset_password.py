from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from ecommerce.authentication.api.v1.serializers.reset_password import PasswordResetSerializer, \
    PasswordResetConfirmSerializer


class PasswordResetView(CreateAPIView):
    """
        Password Reset, if valid email will receive OTP in email
    """
    serializer_class = PasswordResetSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {'detail': 'If an active email account exists in our system , You will get an email shortly'},
            status=status.HTTP_200_OK)


class PasswordResetConfirmView(CreateAPIView):
    """
        Password Reset confirm with OTP received in email
    """
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():  # do not raise error
            self.perform_create(serializer)
            return Response({'detail': 'Password Reset Successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
