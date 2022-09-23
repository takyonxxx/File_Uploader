from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import update_last_login
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, serializers
from rest_framework_simplejwt.serializers import PasswordField, TokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)

from user.models import User
from user.serializers import ldap_authenticate
from user.utils import get_ldap_settings
from rest_framework import exceptions


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        try:
            request = self.context["request"]
        except KeyError:
            pass
        else:

            authenticate_kwargs = {
                self.username_field: attrs[self.username_field],
                'password': attrs['password'],
            }
            email = request.data.get("email")
            password = request.data.get("password")
            if (email is None) or (password is None):
                raise exceptions.AuthenticationFailed(
                    'username and password required')
            user = User.objects.filter(email=email).first()
            if user is None:
                raise exceptions.AuthenticationFailed('user not found')
            if get_ldap_settings():
                ldap_uri, ldap_dn, ldap_domain, ldap_user_name, ldap_password = get_ldap_settings()
                if ldap_domain in email:
                    is_auth, conn = ldap_authenticate(email, password)
                    if not is_auth:
                        print('deneme')
                        error = 'Ldap authentication failed for user {}'.format(email)
                        raise serializers.ValidationError(error)
                try:
                    authenticate_kwargs['request'] = self.context['request']
                except KeyError:
                    pass
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        return data

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
