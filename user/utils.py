import datetime

import jwt
from django.conf import settings


def generate_access_token(user):
    access_token_payload = {
        'id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1, minutes=5),
        'iat': datetime.datetime.utcnow(),
    }
    access_token = jwt.encode(access_token_payload,
                              settings.SECRET_KEY, algorithm='HS256')
    return access_token


def generate_refresh_token(user):
    refresh_token_payload = {
        'id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
        'iat': datetime.datetime.utcnow()
    }
    refresh_token = jwt.encode(
        refresh_token_payload, settings.SECRET_KEY, algorithm='HS256')

    return refresh_token


def find_child(children):
    tmp_list = []
    for child in children:
        id = child['id']
        for item in children:
            if item['parent_organization'] != item.id:
                tmp_list.append(child)
    return list(tmp_list)
