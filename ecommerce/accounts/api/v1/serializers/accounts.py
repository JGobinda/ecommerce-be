from rest_framework import serializers

from ecommerce.accounts.models import User
from ecommerce.commons.serializers import DynamicFieldsModelSerializer


class UserSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'name', 'is_active', 'groups', 'last_activity',
                  'updated_at', 'profile_picture', 'phone_number', 'gender', 'dob', 'receive_offer')
        read_only_fields = 'username', 'email', 'last_activity', 'updated_at',

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')
        if request and request.method.lower() == 'get':
            fields['profile_picture'] = serializers.URLField(source='profile_picture_thumb')
        if request and request.method.lower() == 'patch':
            fields.pop('groups')
            fields.pop('is_active')
            fields.pop('receive_offer')
        return fields

    @staticmethod
    def get_groups(obj):
        return obj.groups.all().values_list('name', flat=True)

    @staticmethod
    def validate_name(name):
        return name.title()

    @staticmethod
    def validate_phone_number(phone_number):
        import re
        reg_phone_number = re.compile("^(?:98|97|96)\d{8}$")
        if not reg_phone_number.match(phone_number):
            raise serializers.ValidationError("Please enter correct phone number!")
        return phone_number


class ProfilePictureUpdateSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = User
        fields = ('profile_picture',)
        extra_kwargs = {
            'profile_picture': {
                'required': True,
                'allow_null': False,
            }
        }