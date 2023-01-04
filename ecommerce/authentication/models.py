from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from knox.models import AuthToken as KnoxAuthTokenModel, AuthTokenManager
from knox.settings import CONSTANTS, knox_settings
from knox import crypto
USER = get_user_model()


class KnoxAuthTokenManager(AuthTokenManager):
    def create(self, user, expiry=knox_settings.TOKEN_TTL, **kwargs):
        token = crypto.create_token_string()
        salt = crypto.create_salt_string()
        digest = crypto.hash_token(token, salt)

        if expiry is not None:
            expiry = timezone.now() + expiry

        instance = super(AuthTokenManager, self).create(
            token_key=token[:CONSTANTS.TOKEN_KEY_LENGTH], digest=digest,
            salt=salt, user=user, expiry=expiry, detail=kwargs.get('detail'))
        return instance, token


class KnoxAuthToken(KnoxAuthTokenModel):
    objects = KnoxAuthTokenManager()
    last_used = models.DateTimeField(null=True, blank=True)
    detail = models.JSONField(null=True, blank=True)

    @classmethod
    def remove_sessions(cls, user_id, exclude=None):
        if exclude is None:
            exclude = []
        return cls.objects.filter(
            user_id=user_id
        ).exclude(
            token_key__in=exclude
        ).delete()
