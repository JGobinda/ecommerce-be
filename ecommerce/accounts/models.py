import os
import uuid
# from urllib.parse import urljoin
#
# from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
# from django.utils.functional import cached_property

from ecommerce.commons.models import TimeStampModel, UUIDBaseModel

from .manager import UserManager
from ..commons.constants import GENDER_CHOICES


def get_profile_picture_upload_path(_, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('user/profile-pictures/', filename)


class User(TimeStampModel, AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()
    username = models.UUIDField(
        max_length=150,
        unique=True,
        validators=[username_validator],
        error_messages={
            'unique': "A user with that username already exists.",
        },
        default=uuid.uuid4
    )
    email = models.EmailField(max_length=45, unique=True, error_messages={
        'unique': "A user with that email already exists.",
    }, )
    name = models.CharField(max_length=80)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    middle_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    phone_number = models.CharField(max_length=14, null=True, blank=True)
    profile_picture = models.ImageField(upload_to=get_profile_picture_upload_path,
                                        null=True, blank=True)
    # last login seems important because, last_activity can only be obtained from AuthToken class
    # if the user deletes all his session , then even this last_activity information is lost
    last_login = models.DateTimeField('last login', blank=True, null=True)
    last_activity = models.DateTimeField('last activity', blank=True, null=True)
    is_active = models.BooleanField(default=False)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=20, blank=True, null=True)
    dob = models.DateField(blank=True, null=True
                           )
    receive_offer = models.BooleanField(default=True)
    notification = models.BooleanField(default=True)
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    ACCOUNT_REGISTRATION_FIELDS = ['email', 'name', 'phone_number', 'password']

    _send_password_change_email = False
    add_this_password_to_history = None

    # pylint: disable=W0201
    def set_password(self, raw_password):
        super().set_password(raw_password)
        self.add_this_password_to_history = self.password

    # pylint: disable=C0415
    # @cached_property
    # def permission_codes(self):
    #     from spark.permission.models import SparkPermission
    #     groups = self.groups.all()
    #     permissions = SparkPermission.objects.filter(
    #         groups__in=groups
    #     ).values_list('code', flat=True)
    #     return set(permissions)

    # # pylint: disable=C0415
    # @cached_property
    # def humanized_permission_codes(self):
    #     from spark.permission.models import SparkPermission
    #     groups = self.groups.all()
    #     permissions = SparkPermission.objects.filter(
    #         groups__in=groups
    #     ).values_list('humanized_var', flat=True)
    #     return set(permissions)

    @property
    def profile_picture_thumb(self):
        if self.profile_picture:
            return self.profile_picture.url

        from django.templatetags.static import static
        return static('user/images/default_user.jpg')

    @property
    def is_staff(self):
        return self.is_superuser

    @property
    def user_groups(self):
        try:
            groups = self.groups.all().values_list('name', flat=True)
        except:
            groups = []
        return groups

    def __str__(self):
        return f"{self.email}"

    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        instance = super().save(*args, **kwargs)
        return instance


class UserLoginMeta(TimeStampModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userloginmeta")
    user_agent = models.TextField(null=True, blank=True)
    # max length for IPV6 is 39, including the colon (:) character
    ip_address = models.CharField(max_length=39, null=True, blank=True)
    private_ip = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return f'Login meta for user => {self.user.email}'




