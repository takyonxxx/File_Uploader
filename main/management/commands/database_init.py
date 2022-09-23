from django.core.cache import cache
from django.core.management.base import BaseCommand

from document.models import ConnectionPropertyType, Connector
from user.models import Module, Permission


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.add_modules(),
        self.add_connectors(),
        self.add_connection_properties(),
        self.clear_cache()

    def clear_cache(self):
        print('Cleaning cached values...')
        for key in cache.keys('*'):
            cache.delete(key)

    def add_modules(self):
        self.stdout.write(self.style.NOTICE('Default Modules migrating...'))
        default_modules = [
            {
                'name': 'Users',
                'slug': 'User',
            },
            {
                'name': 'Roles',
                'slug': 'Role',
            },
            {
                'name': 'Repositories',
                'slug': 'Repository',
            },
            {
                'name': 'Settings',
                'slug': 'Setting',
            },
            {
                'name': 'Connectors',
                'slug': 'Connector'
            },
        ]
        default_permissions = ['Read', 'Write']
        Module.objects.all().delete()
        Permission.objects.all().delete()
        for module in default_modules:
            new_module, created = Module.objects.get_or_create(**module)
            for permission in default_permissions:
                new_perm = Permission(

                    name=permission,
                    slug=permission.lower() + new_module.slug,
                    module_id=new_module.id

                )
                new_perm.save()

    def add_connectors(self):

        self.stdout.write(self.style.NOTICE('Default Connectors migrating...'))
        default_settings = [
            {
                'id': 1,
                'name': 'File System',
            },
        ]
        for item in default_settings:
            Connector.objects.get_or_create(**item)

    def add_connection_properties(self):

        self.stdout.write(self.style.NOTICE('Default Connection Properties migrating...'))
        default_settings = [
            {
                'id': 1,
                'name': 'UNC Path',
                'type': 'unc_path',
                'data_type': 'text',
                'is_required': True,
                'connector_id': 1,
            },

        ]
        for item in default_settings:
            ConnectionPropertyType.objects.update_or_create(
                id=item.get('id'),
                defaults={**item},
            )
