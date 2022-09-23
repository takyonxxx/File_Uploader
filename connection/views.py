from connection.serializers import (ConnectionPropertyTypeSerializer,
                                    ConnectorSerializer)
from document.models import ConnectionPropertyType, Connector
from main.base_view import BaseViewSet
from user.permissions import CustomPermission


class ConnectorPropertyTypeViewSet(BaseViewSet):
    queryset = ConnectionPropertyType.objects.all()
    serializer_class = ConnectionPropertyTypeSerializer


class ConnectorViewSet(BaseViewSet):
    queryset = Connector.objects.all()
    serializer_class = ConnectorSerializer
    search_fields = ['name', 'accessibility', 'integrity', 'probability', 'fields', 'risk_score']
    permission_classes = [CustomPermission]
