from rest_framework import exceptions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import APIException
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from main.base_view import BaseViewSet
from user.filters import UserFilter
from user.models import Module, Permission, Role, User
from user.permissions import CustomPermission, FunctionPermission
from user.serializers import (ModuleSerializer, PermissionSerializer,
                              RoleSerializer, UserSerializer,
                              UserWithPermissionSerializer)


class PermissionViewSet(BaseViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer


class ModuleViewSet(BaseViewSet):
    queryset = Module.objects.all()
    permissions = ['readRole', 'writeRole']
    permission_classes = [CustomPermission]
    serializer_class = ModuleSerializer


class RoleViewSet(BaseViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [CustomPermission]
    search_fields = ['name']


class UserViewSet(BaseViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permissions = ['viewUser']
    permission_classes = [CustomPermission]
    filter_backends = [UserFilter]
    search_fields = ['first_name', 'last_name', 'email']


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    email = request.data.get('email')
    password = request.data.get('password')
    if (email is None) or (password is None):
        raise exceptions.AuthenticationFailed(
            'Email and Password required')
    user = User.objects.filter(email=email).first()
    if user is None:
        raise exceptions.AuthenticationFailed('User not found')
    if user.is_superuser:
        is_auth = user.check_password(password)
        if not is_auth:
            raise exceptions.AuthenticationFailed('Provided credentials are not valid')

    refresh = RefreshToken.for_user(user)

    return Response({
        'access': str(refresh.access_token),
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def current_user(request):
    user = request.user
    if not user.is_anonymous:
        serializer = UserWithPermissionSerializer(user)
        return Response(serializer.data)
    else:
        raise APIException('User should be authenticated!')

