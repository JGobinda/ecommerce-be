import re
from django.db import transaction
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password as dj_validate_password
from rest_framework import serializers

from ecommerce.commons.serializers import DynamicFieldsModelSerializer


USER = get_user_model()


class UserAccountRegistrationSerializer(DynamicFieldsModelSerializer):
    repeat_password = serializers.CharField(max_length=128, write_only=True,
                                            style={'input_type': 'password'})
    name = serializers.CharField(max_length=200, required=False)
    email = serializers.EmailField()

    class Meta:
        model = USER
        fields = ['first_name', 'middle_name', 'last_name', 'repeat_password'] + USER.ACCOUNT_REGISTRATION_FIELDS
        extra_kwargs = {
            'password': {
                'write_only': True
            },
            'phone_number': {
                'required': True
            }
        }

    @staticmethod
    def validate_password(password):
        dj_validate_password(password)
        return password

    # FOR PHONE_NUMBER VALIDATION
    @staticmethod
    def validate_phone_number(phone_number):
        if not phone_number:
            raise serializers.ValidationError({
                'Error': "Please enter your phone number."
            })
        reg_phone_number = re.compile("^(?:98|97|96)\d{8}$")
        if not reg_phone_number.match(phone_number):
            raise serializers.ValidationError("Please enter correct phone number")
        return phone_number

    @staticmethod
    def validate_email(email):
        user = USER.objects.filter(email=email, is_active=True)
        if user.exists():
            raise serializers.ValidationError("A user with that email already exists!")
        return email

    def validate(self, attrs):
        if attrs['password'] != attrs['repeat_password']:
            raise serializers.ValidationError({'repeat_password': 'Does not match with password'})

        if 'name' not in attrs:
            if 'first_name' not in attrs or 'last_name' not in attrs:
                raise serializers.ValidationError('First name and Last name is required.')
            else:
                if 'middle_name' in attrs:
                    attrs['name'] = f"{attrs['first_name']} {attrs['middle_name']} {attrs['last_name']}"
                else:
                    attrs['name'] = f"{attrs['first_name']} {attrs['last_name']}"
        else:
            names = attrs['name'].split(' ')
            if len(names) == 3:
                attrs['first_name'] = names[0]
                attrs['middle_name'] = names[1]
                attrs['last_name'] = names[2]
            if len(names) == 2:
                attrs['first_name'] = names[0]
                attrs['last_name'] = names[1]
        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            _ = validated_data.pop('repeat_password')
            password = validated_data.pop('password')
            instance = super().create(validated_data)

            instance.set_password(password)
            instance.save()
            # instance.groups.add(
            #     Group.objects.get(name__iexact=NORMAL_USER)
            # )
            if getattr(settings, 'USER_TEST_MODE', False):
                instance.is_active = True
                instance.save()
            instance.is_active = True
            # else:
            #     send_account_activation_otp_to_email(instance)
            return instance

