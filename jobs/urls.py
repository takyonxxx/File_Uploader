from django.urls import path
from . import views


urlpatterns = [
    path('start_logs_scheduler/', views.start_logs_scheduler, name='start_logs_scheduler'),
    path('stop_logs_scheduler/', views.stop_logs_scheduler, name='stop_logs_scheduler'),
]
