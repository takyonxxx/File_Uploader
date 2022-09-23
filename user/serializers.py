from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from user.models import Module, Permission, Role, User


class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id']

    def to_representation(self, obj):
        return obj.id


class PermissionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'slug', 'module_id']


class ModuleSerializer(serializers.ModelSerializer):
    children = PermissionDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = ['id', 'name', 'slug', 'children']


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'permissions']


class RoleDetailSerializer(serializers.ModelSerializer):
    permissions = PermissionDetailSerializer(many=True, read_only=True, )

    class Meta:
        model = Role
        fields = ['id', 'name', 'permissions']


class UserSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        instance = super(UserSerializer, self).create(validated_data)
        if 'password' in self.initial_data:
            instance.password = make_password(self.initial_data.get('password'))
            instance.save()
        return instance

    class Meta:
        model = User
        exclude = ('password',)
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 1},
            'domain': {'read_only': True}
        }


class UserWithPermissionSerializer(serializers.ModelSerializer):
    roles = RoleDetailSerializer(many=True, read_only=True)

    class Meta:
        model = User
        exclude = ('password',)
        extra_kwargs = {'password': {'write_only': True, 'min_length': 1}}
