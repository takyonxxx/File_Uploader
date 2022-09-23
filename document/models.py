import uuid

from django.db import models
from django.utils import timezone
from rest_framework import serializers


class InternalPkModelSerializer(serializers.ModelSerializer):
    _intended_depth = None

    def __init__(self, *args, **kwargs):
        self._intended_depth = self._intended_depth or self.Meta.depth

        self.nested_create = self.Meta.nested_create

        if self.nested_create:
            for _field in self.Meta.model._meta.get_fields():
                is_foreign_key = isinstance(_field, models.ForeignKey)
                is_received = isinstance(kwargs.get('data', {}).get(_field.name, False), dict)
                if all([is_received, is_foreign_key]):
                    setattr(self, _field.name, _field.remote_field.model.get_serializer())
                    self.Meta.read_only_fields += (_field.name,)

        super().__init__(*args, **kwargs)
        if getattr(self, 'initial_data', None):
            self.Meta.depth = 0
        else:
            self.Meta.depth = self._intended_depth or 1

    def build_nested_field(self, field_name, relation_info, nested_depth):
        """
        Create nested fields for forward and reverse relationships.
        """

        def get_nested_relation_kwargs(_info):
            kwargs = {'read_only': True}
            if _info.to_many:
                kwargs['many'] = True
            return kwargs

        class NestedSerializer(serializers.ModelSerializer):
            class Meta:
                model = relation_info.related_model
                depth = nested_depth - 1
                fields = '__all__'

        field_class = NestedSerializer
        field_kwargs = get_nested_relation_kwargs(relation_info)

        return field_class, field_kwargs

    def create(self, validated_data):
        if self.nested_create:
            for _field in self.Meta.model._meta.get_fields():
                if isinstance(_field, models.ForeignKey) and _field.name in self.initial_data.keys():
                    nested_serializer = _field.remote_field.model.get_serializer()(
                        data=self.initial_data.get(_field.name)
                    )
                    nested_serializer.is_valid(raise_exception=True)
                    nested_instance = nested_serializer.create(nested_serializer.validated_data)
                    validated_data[f'{_field.name}_id'] = nested_instance.pk

        return super().create(validated_data)

    def update(self, instance, validated_data):
        if self.nested_create:
            for _field in self.Meta.model._meta.get_fields():
                if isinstance(_field, models.ForeignKey) and _field.name in self.initial_data.keys():
                    nested_serializer = _field.remote_field.model.get_serializer()(
                        instance=getattr(instance, _field.name), data=self.initial_data.get(_field.name)
                    )
                    nested_serializer.is_valid(raise_exception=True)
                    nested_instance = nested_serializer.save()
                    validated_data[f'{_field.name}_id'] = nested_instance.pk
        return super().update(instance, validated_data)

    def is_valid(self, raise_exception=False):
        return super().is_valid(raise_exception=raise_exception)

    class Meta:
        model = None
        nested_create = False
        read_only_fields = tuple()


class AppBaseModel(models.Model):
    @classmethod
    def get_serializer(cls, fields: tuple = None, exclude: tuple = None, additional_fields: dict = None, depth=1,
                       id_required=False, nested_create=False, use_internal_pk=False):
        """
            Monkey-patch to add class method to embedded library Model classes
            Not the best practice, will be refactored later
        """
        if not (fields or exclude):
            fields = '__all__'

        assert not (fields and exclude), 'You cannot use a model serializer with both fields and exclude declared'
        serializer_model = InternalPkModelSerializer if use_internal_pk else serializers.ModelSerializer
        return type(
            f'{cls.__name__}Serializer', (serializer_model,),
            {
                **({'id': serializers.CharField(required=id_required)}
                   if (exclude and ('id' not in exclude)
                       or (fields and ('id' in fields)))
                   else {}),
                **(additional_fields or {}),
                'Meta': type('Meta', (), {
                    'model': cls, 'fields': fields if fields else None,
                    'exclude': exclude, 'depth': depth, 'nested_create': nested_create,
                }),
            }
        )

    class Meta:
        abstract = True


class Connector(AppBaseModel):
    name = models.CharField(max_length=255, )
    accessibility = models.IntegerField(default=1, null=True, blank=True)
    integrity = models.IntegerField(default=1, null=True, blank=True)
    probability = models.IntegerField(default=1, null=True, blank=True)

    class Meta:
        db_table = 'connectors'


class ConnectionPropertyType(models.Model):
    connector = models.ForeignKey(Connector, related_name='fields', on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=255, )
    type = models.CharField(max_length=255, )
    data_type = models.CharField(max_length=255, )
    is_required = models.BooleanField(default=True)

    class Meta:
        db_table = 'connection_property_types'


class ConnectionPropertyTypeOption(models.Model):
    connection_property = models.ForeignKey(ConnectionPropertyType, on_delete=models.CASCADE, null=True)
    text = models.CharField(max_length=255, )

    class Meta:
        db_table = 'connection_property_type_options'
        ordering = ('id',)


class Repository(models.Model):
    FREQUENCY_CHOICES = (
        (1, 'Daily'),
        (2, 'Weekly'),
        (3, 'Monthly')
    )
    name = models.CharField(max_length=255)
    frequency = models.IntegerField(choices=FREQUENCY_CHOICES, default=1, null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    is_full_index = models.BooleanField(default=False, null=True, blank=True)
    connector = models.ForeignKey(Connector, on_delete=models.CASCADE, default=1)
    created = models.DateTimeField(default=timezone.localtime)
    risk_score = models.IntegerField(default=1, null=True, blank=True)

    class Meta:
        unique_together = ['name', 'connector']
        db_table = 'repositories'


class RepositoryMetadata(models.Model):
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, null=True)
    schema = models.TextField(null=True)
    folders = models.TextField(null=True)
    created = models.DateTimeField(default=timezone.localtime)

    class Meta:
        db_table = 'repository_metadata'
        ordering = ('id',)


class RepositoryItemType(models.Model):
    type = models.CharField(max_length=255, )

    class Meta:
        db_table = 'repository_item_types'


class ConnectionInfo(models.Model):
    connection_property = models.ForeignKey(ConnectionPropertyType, on_delete=models.CASCADE, null=True)
    repository = models.ForeignKey(Repository, related_name='fields', on_delete=models.CASCADE, null=True)
    value = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = 'connections'


class RepositoryItem(models.Model):
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, null=True)
    item_type = models.ForeignKey(RepositoryItemType, on_delete=models.CASCADE, null=True)
    start_date = models.DateTimeField()
    is_full_index = models.BooleanField(default=True)

    class Meta:
        db_table = 'repository_items'


class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source = models.CharField(max_length=200)
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, null=True, related_name='documents')
    name = models.CharField(max_length=200)
    path = models.CharField(max_length=200, default='/')
    dir_path = models.CharField(max_length=200, default='/')
    dir_len = models.IntegerField(null=True)
    path_len = models.IntegerField(null=True)
    size = models.IntegerField(null=True)
    content = models.TextField(null=True)
    is_undiscovered = models.BooleanField(default=False)
    file_content_vector = models.TextField(blank=True, null=True)
    file_path_vector = models.TextField(blank=True, null=True)
    file_author_vector = models.TextField(blank=True, null=True)
    file_date_vector = models.TextField(blank=True, null=True)
    file_size_vector = models.TextField(blank=True, null=True)
    file_category_vector = models.TextField(blank=True, null=True)
    file_developer_vector = models.TextField(blank=True, null=True)
    file_program_vector = models.TextField(blank=True, null=True)
    last_access_time = models.DateTimeField(default=timezone.localtime, null=True)
    created = models.DateTimeField(default=timezone.localtime)
    data_types = models.ManyToManyField('document.DataType', blank=True, related_name='documents')
    risk_score = models.IntegerField(default=1, null=True, blank=True)

    class Meta:
        unique_together = ['repository', 'path']
        db_table = 'documents'
        ordering = ('-source',)


class DataCategory(models.Model):
    name = models.CharField(max_length=200)
    weight = models.IntegerField(default=0)
    code = models.CharField(max_length=50, default='')
    created = models.DateTimeField(default=timezone.localtime)

    class Meta:
        db_table = 'data_categories'


class DataType(models.Model):
    name = models.CharField(max_length=255, )
    threshold = models.IntegerField(default=0)
    risk_level = models.IntegerField(default=0)
    aliases = models.CharField(max_length=255, default='')
    category = models.ForeignKey(DataCategory, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'data_types'
