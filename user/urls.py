from django.urls import path

from main.base_view import create_view_paths
from user import views

urlpatterns = [
    path('login/', views.login_view),
    path('currentUser/', views.current_user, name='current_user'),

    *create_view_paths('User', views.UserViewSet),
    *create_view_paths('Role', views.RoleViewSet),
    *create_view_paths('Permission', views.PermissionViewSet),
]
