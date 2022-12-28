from config import settings
from hashids import Hashids

HASH_IDS = Hashids(salt=settings.SECRET_KEY, min_length=5)


def id_encode(to_be_encoded):
    return HASH_IDS.encode(to_be_encoded)


def id_decode(to_be_decoded):
    return HASH_IDS.decode(to_be_decoded)
