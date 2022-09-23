from rest_framework import exceptions, serializers

from document.models import (ConnectionInfo, ConnectionPropertyType, Connector,
                             Repository)
from document.serializers import DocumentDetailSerializer


class ConnectionPropertyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConnectionPropertyType
        fields = ['id', 'name', 'type', 'data_type', 'is_required']


class ConnectorSerializer(serializers.ModelSerializer):
    fields = serializers.SerializerMethodField(read_only=True, method_name='get_properties')

    class Meta:
        model = Connector
        fields = ['id', 'name', 'fields', 'accessibility', 'integrity', 'probability']

    @staticmethod
    def get_properties(instance):
        connection_properties = instance.fields.all().order_by('id')
        return ConnectionPropertyTypeSerializer(connection_properties, many=True).data


class ConnectorSlimSerializer(serializers.ModelSerializer):
    class Meta:
        model = Connector
        fields = ['id', 'name']


class ConnectionInfoSerializer(serializers.ModelSerializer):
    connection_property = ConnectionPropertyTypeSerializer(read_only=True)

    class Meta:
        model = ConnectionInfo
        fields = ['id', 'value', 'connection_property']


class RepositorySerializer(serializers.ModelSerializer):
    fields = ConnectionInfoSerializer(many=True, read_only=True)

    def check_uniqueness(self, fields):
        # File System
        # Inputs : UNC path
        if self.data['connector'] == 1:
            check_connection_data = ConnectionInfo.objects.filter(
                value=fields[0].get('value'),
                connection_property_id=fields[0].get('id'),
            )
            if len(check_connection_data) == 1:
                return self.data.get('id') == check_connection_data[0].repository_id
            elif len(check_connection_data) > 0:
                # raise exceptions.ValidationError({'detail': 'Connection already exists'})
                return False
        else:
            field_values = {}
            for field in fields:
                field_values[field.get('type')] = (field.get('id'), field.get('value'))

            matched_server = ConnectionInfo.objects.filter(
                value=field_values['server'][1],
                connection_property_id=field_values['server'][0],
            )

            # Exchange Server
            # Inputs : Server - Email
            if self.data['connector'] == 2:
                matched_email = ConnectionInfo.objects.filter(
                    value=field_values['email'][1],
                    connection_property_id=field_values['email'][0],
                    repository_id__in=[s.repository_id for s in matched_server]
                )
                if len(matched_email) == 1:
                    return self.data.get('id') == matched_email[0].repository_id
                if len(matched_email) > 0:
                    # raise exceptions.ValidationError({'detail': 'Connection already exists'})
                    return False

            # Database Server
            # Inputs : Server - DB name - Username
            if self.data['connector'] == 3:
                matched_dbname = ConnectionInfo.objects.filter(
                    value=field_values['db_name'][1],
                    connection_property_id=field_values['db_name'][0],
                    repository_id__in=[s.repository_id for s in matched_server]
                )
                matched_username = ConnectionInfo.objects.filter(
                    value=field_values['user_name'][1],
                    connection_property_id=field_values['user_name'][0],
                    repository_id__in=[s.repository_id for s in matched_dbname]
                )
                if len(matched_username) == 1:
                    return self.data.get('id') == matched_username[0].repository_id
                if len(matched_username) > 0 and len(matched_dbname) > 0:
                    # raise exceptions.ValidationError({'detail': 'Connection already exists'})
                    return False
        return True

    def create(self, validated_data):
        fields = self.initial_data.get('fields')
        is_unique = self.check_uniqueness(fields=fields)

        if is_unique:
            instance = super(RepositorySerializer, self).create(validated_data)
            if fields is not None and isinstance(fields, list):
                for field in fields:
                    ConnectionInfo.objects.create(value=field.get('value'), connection_property_id=field.get('id'),
                                                  repository_id=instance.id)
            return instance
        else:
            raise exceptions.ValidationError({'detail': 'Repository already exists.'})

    def update(self, instance, validated_data):
        fields = self.initial_data.get('fields')
        is_unique = self.check_uniqueness(fields=fields)

        if is_unique:
            instance = super(RepositorySerializer, self).update(instance, validated_data)
            ConnectionInfo.objects.filter(repository_id=instance.id).delete()
            if fields is not None and isinstance(fields, list):
                for field in fields:
                    ConnectionInfo.objects.create(value=field.get('value'),
                                                  connection_property_id=field.get('id'),
                                                  repository_id=instance.id)
            return instance
        else:
            raise exceptions.ValidationError({'detail': 'Repository already exists.'})

    class Meta:
        model = Repository
        fields = [
            'id',
            'name',
            'frequency',
            'connector',
            'start_date',
            'is_full_index',
            'fields',
            'risk_score',
        ]


class RepositoryDetailSerializer(serializers.ModelSerializer):
    documents = DocumentDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Repository
        fields = ['connector', 'id', 'name', 'documents']


class RepositorySlimSerializer(serializers.ModelSerializer):

    class Meta:
        model = Repository
        fields = '__all__'
