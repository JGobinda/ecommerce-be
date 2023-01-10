from rest_framework.generics import CreateAPIView
from ..serializers.user_activation import UserAccountActivationWithOTPSerializer
from rest_framework.response import Response


class UserAccountActivationWithOTPView(CreateAPIView):
    serializer_class = UserAccountActivationWithOTPSerializer
    permission_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'detail': 'Account has been activated'
        })
