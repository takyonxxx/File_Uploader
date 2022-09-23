from rest_framework import serializers

from document.models import (Document)


class FilteredListSerializer(serializers.ListSerializer):
    filter_kwargs = {}

    def to_representation(self, data):
        if not self.filter_kwargs or not isinstance(self.filter_kwargs, dict):
            raise TypeError('Invalid Attribute Type: `filter_kwargs` must be a of type `dict`.')
        data = data.filter(**self.filter_kwargs)
        return super().to_representation(data)


class DocumentSerializer(serializers.ModelSerializer):
    repository_name = serializers.CharField(source='repository.name')

    class Meta:
        model = Document
        fields = '__all__'
        depth = 1


class DocumentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'path', 'name']

