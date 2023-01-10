from datetime import datetime, timezone, timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from ecommerce.authentication.models import UserOTPVerification

USER = get_user_model()


class UserAccountActivationWithOTPSerializer(serializers.Serializer):
    otp = serializers.IntegerField()
    email = serializers.EmailField()
    user = None

    @staticmethod
    def validate_email(email):
        user = USER.objects.filter(email__iexact=email)
        if not user.exists():
            raise serializers.ValidationError("Invalid Email")
        return email

    def validate(self, attrs):
        otp = attrs.get('otp')
        email = attrs.get('email')
        if not email:
            raise serializers.ValidationError("Please enter your email.")

        try:
            self.user = USER.objects.get(email__exact=email)
        except ObjectDoesNotExist:
            raise serializers.ValidationError("Invalid Email")

        if self.user.is_active:
            raise serializers.ValidationError("User is already activated")

        if not UserOTPVerification.objects.filter(otp__exact=otp, email__exact=email).exists():
            raise serializers.ValidationError('Invalid OTP!')
        else:
            user_otp = UserOTPVerification.objects.filter(otp__exact=otp, email__exact=email).latest('created_at')
            if user_otp.is_expired or user_otp.is_verified or \
                    (user_otp.created_at < datetime.now(timezone.utc) - timedelta(days=1)):
                user_otp.is_expired = True
                user_otp.save()
                raise serializers.ValidationError('Your OTP has expired. Please request for new OTP.')
            return attrs

    def create(self, validated_data):
        if not self.user.is_active:
            self.user.is_active = True
            user_otp_verification = UserOTPVerification.objects.filter(otp__exact=validated_data['otp'],
                                                                       email=validated_data['email'],
                                                                       is_expired=False).latest('created_at')
            user_otp_verification.is_expired = True
            user_otp_verification.save()
        self.user.save()
        return self.user
