import itertools

from django.urls import path

from main.base_view import create_view_paths

from . import views


def flatten_list(nested_list):
    return itertools.chain.from_iterable(nested_list)


urlpatterns = [
    path('search_elastic/', views.search_elastic, name='search_elastic'),
    path('delete_files/', views.delete_files, name='delete_files'),
    path('refresh_connections/', views.refresh_connections, name='refresh_connections'),
    path('get_document_content/', views.get_document_content, name='get_document_content'),
    path('get_cached_status/', views.get_cached_status, name='get_cached_status'),

    *flatten_list(
        create_view_paths(_name, getattr(views, f'{_name}ViewSet'))
        for _name in [
            'Document',
            'Repository',
            'CacheController',
            'ProcessController',
        ]
    )

]
