import math
import os
import random
import string
import uuid
from binascii import hexlify
from datetime import timezone

from aead import AEAD

from main import settings


def utc_to_local(utc_dt):
    try:
        a = utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)
    except Exception as e:
        print(e)
        return utc_dt
    return a


def local_to_utc(local_dt):
    return local_dt.astimezone(timezone.utc)


def validate_request(reqiureddict, obj):
    for d in reqiureddict:
        if d not in obj:
            raise Exception('Please set required fields')


def choice_parser(choices):
    return [{"id": choice[0], "value": choice[1]} for choice in choices]


def generate_pk(prefix, upper=False, length=15, separator="-"):
    chars = "%s%s%s%s" % (
        string.ascii_uppercase, string.digits, uuid.uuid1().hex, hexlify(os.urandom(16)).decode("utf-8"))
    pk = prefix.lower() + separator + "".join(random.choice(chars) for _ in range(length)).lower()
    if upper:
        pk = pk.upper()
    return pk


def generate_crypto_key():
    return AEAD.generate_key()


def encrypt_string(val, key):
    try:
        cryptor = AEAD(key)
        ct = cryptor.encrypt(val.encode('utf-8'), settings.SECRET_KEY.encode('utf-8'))
        return ct
    except Exception as e:
        print(e)
        return ''


def decrypt_string(val, key):
    try:
        cryptor = AEAD(key)
        ct = cryptor.decrypt(val, settings.SECRET_KEY.encode('utf-8'))
        return ct.decode('utf-8')

    except Exception as e:
        print(e)
        return ''


def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


def get_common_path(path_list):
    """Given a list of paths, returns the longest common leading component"""
    if not path_list:
        return ''
    s1 = min(path_list)
    s2 = max(path_list)
    for i, c in enumerate(s1):
        if c != s2[i]:
            return '/'.join(s1[:i].split('/')[:-1])
    return '/'.join(s1.split('/')[:-1])
