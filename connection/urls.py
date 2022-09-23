from main.base_view import create_view_paths
from connection import views


urlpatterns = [
    *create_view_paths('Connector', views.ConnectorViewSet),
    *create_view_paths('ConnectorPropertyType', views.ConnectorPropertyTypeViewSet),
]
