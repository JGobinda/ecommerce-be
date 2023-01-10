from datetime import datetime, timezone, timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password as dj_validate_password
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework import status


from ecommerce.authentication.models import UserOTPVerification
from ecommerce.authentication.utils import send_password_reset_email

USER = get_user_model()


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    @staticmethod
    def validate_email(email):
        user = USER.objects.filter(email__iexact=email).first()
        if not user:
            raise serializers.ValidationError({
                'detail': 'Invalid Email'
            }, code=status.HTTP_404_NOT_FOUND)
        if not user.is_active:
            raise serializers.ValidationError({
                'detail': 'Inactive user'
            })
        return email

    def create(self, validated_data):
        email = validated_data.get('email')
        otp_request = None
        if email:
            user = USER.objects.filter(email__iexact=email).first()
            if UserOTPVerification.objects.filter(email__iexact=email).exists():
                last_otp = UserOTPVerification.objects.filter(email__iexact=email).latest('created_at')
                last_otp.is_expired = True
                last_otp.save()
            otp_request = send_password_reset_email(user)
        return otp_request


class PasswordResetConfirmSerializer(PasswordResetSerializer):
    password = serializers.CharField(max_length=128, write_only=True,
                                     style={'input_type': 'password'})
    repeat_password = serializers.CharField(max_length=128, write_only=True,
                                            style={'input_type': 'password'})
    email = serializers.CharField(max_length=50, help_text='Enter your email address')
    otp = serializers.IntegerField()

    @staticmethod
    def validate_password(password):
        dj_validate_password(password)
        return password

    @staticmethod
    def validate_email(email):
        user = USER.objects.filter(email__iexact=email)
        if not user.exists():
            raise serializers.ValidationError("Invalid Email")
        return email

    def validate(self, attrs):
        if len(str(attrs['otp'])) != 6:
            raise serializers.ValidationError('OTP must be of 6 digits.')
        email = attrs.get('email')
        if not email:
            raise serializers.ValidationError('Email is required')
        try:
            user_otp = UserOTPVerification.objects.filter(email=email).latest('created_at')
            if user_otp:
                if user_otp.otp != attrs['otp']:
                    raise serializers.ValidationError("OTP is invalid. Please enter a correct OTP.")
        except ObjectDoesNotExist:
            raise serializers.ValidationError('Invalid Email')

        if (user_otp.is_expired or user_otp.is_verified or
                (user_otp.created_at < datetime.now(timezone.utc) - timedelta(days=1))):
            attrs['is_expired'] = True
            raise serializers.ValidationError({'detail': 'The OTP has already expired.'})
        else:
            if attrs['password'] != attrs['repeat_password']:
                raise serializers.ValidationError({'new_password': "Passwords doesn't match."})

        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            email = validated_data.get('email')
            password = validated_data.get('password')
            if email:
                user = USER.objects.get(email=email)
                user.set_password(password)
                UserOTPVerification.objects.filter(email=email).update(is_verified=True, is_expired=True)
            user.save()
        return validated_data
