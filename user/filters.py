from rest_framework.filters import BaseFilterBackend
from django.db.models import Q


class UserFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        user = request.user
        return queryset.filter(is_superuser=False)
