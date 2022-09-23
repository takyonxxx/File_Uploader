from rest_framework.permissions import BasePermission

from user.models import Permission


def get_permissions(user):
    permissions = Permission.objects.filter(role__user=user)
    return permissions.distinct()


class CustomPermission(BasePermission):

    def has_permission(self, request, view):
        user = request.user
        if user.is_superuser:
            return True
        permissions = get_permissions(user)
        action = getattr(view, 'action', None)
        custom_permissions = getattr(view, 'permissions', None)
        module = view.queryset.model.__name__
        if getattr(view, 'override_module', False):
            module = view.override_module

        if action in ['list', 'retrieve']:
            if permissions.filter(slug='read' + module):
                return True
            if custom_permissions:
                if permissions.filter(slug__in=custom_permissions):
                    return True

        elif action in ['create', 'update', 'destroy', 'bulk_create', 'bulk_update']:
            if permissions.filter(slug='write' + module):
                return True
            else:
                return False


class FunctionPermission(BasePermission):
    permission_codename = ''

    def __init__(self, permission_codename):
        super().__init__()
        self.permission_codename = permission_codename

    def __call__(self):
        return self

    def has_permission(self, request, view):
        user = request.user
        if user.is_superuser:
            return True
        permissions = get_permissions(user)
        user_roles = permissions.values_list('slug', flat=True)
        if set(self.permission_codename).issubset(user_roles):
            return True
        else:
            return False
