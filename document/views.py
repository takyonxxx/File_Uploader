import json
import logging
import multiprocessing

from django.core.cache import cache
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from connection.serializers import RepositorySerializer
from document.connectors import stop_connectors, update_connections_thread
from document.models import Document, Repository
from document.serializers import (DocumentSerializer)
from main.base_view import BaseViewSet
from user.permissions import CustomPermission, FunctionPermission

logger = logging.getLogger(__name__)


class ProcessControllerViewSet(viewsets.ViewSet):

    def destroy(self, request):
        print('Stopping all connectors..')
        connectors_stopped = stop_connectors()
        print('Clearing all cached items..')
        cache_cleared = CacheControllerViewSet().clear_all()
        for p in multiprocessing.active_children():
            p.terminate()
        print('Cleared all connections, processes and cached items.')
        return Response(
            {'status': connectors_stopped and cache_cleared},
            status=status.HTTP_200_OK
        )


class CacheControllerViewSet(viewsets.ViewSet):
    def clear_all(self):
        for key in cache.keys('*'):
            cache.delete(key)
            logger.debug(f'Deleted {key} from cache.')
        return True

    def list(self, request):
        return Response({'cached_items': cache.keys('*')}, status=status.HTTP_200_OK)

    def create(self, request):
        key = request.data.get('key') or ''
        value = request.data.get('value') or ''
        expires_in = request.data.get('expires_in') or ''
        if key and value and expires_in:
            if not cache.get(key):
                cache.set(key, value, expires_in)
            else:
                return Response(
                    {'status': False, 'error': 'Cache already exists.'},
                    status=status.HTTP_202_ACCEPTED
                )
        else:
            return Response(
                {'status': False, 'error': 'Invalid parameters detected.'},
                status=status.HTTP_200_OK
            )
        return Response({'status': True}, status=status.HTTP_201_CREATED)

    def retrieve(self, request):
        key = request.data.get('key') or ''
        if key and cache.get(key):
            return Response({'status': True, key: cache.get(key)}, status=status.HTTP_200_OK)
        else:
            return Response({'status': False}, status=status.HTTP_200_OK)

    def destroy(self, request):
        key = request.data.get('key') or ''
        if key and cache.get(key):
            cache.delete(key)
            return Response({'status': True}, status=status.HTTP_200_OK)
        else:
            return Response({'status': False}, status=status.HTTP_200_OK)


class DocumentViewSet(BaseViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = (IsAuthenticated,)
    search_fields = ['id', 'name', 'path', 'repository__name']

    def list(self, request, *args, **kwargs):
        if request.data.get('disable_manuel_data'):
            documents = Document.objects.exclude(
                source__in=['DummyConnector']
            )
        else:
            documents = Document.objects.all()

        documents_ = self.filter_queryset(documents)
        if documents_:
            page = self.paginate_queryset(documents_)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                resp = self.get_paginated_response(serializer.data)
                return resp
        serializer = self.get_serializer(documents_, many=True)

        return Response({'result': serializer.data})


class RepositoryViewSet(BaseViewSet):
    queryset = Repository.objects.exclude(connector__id=4)
    serializer_class = RepositorySerializer
    search_fields = ['name']
    permission_classes = [CustomPermission]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        repo_id = request.data.get('id')
        docs = Document.objects.filter(repository_id=repo_id)
        docs.delete()
        return super(RepositoryViewSet, self).destroy(request, *args, **kwargs)


@api_view(['POST'])
@permission_classes([
    IsAuthenticated,
])
def delete_files(request):
    params = json.loads(request.body.decode('utf-8'))
    document_list = list(params)
    deleted_files = list()
    if len(document_list) > 0:
        for doc_id in document_list:
            document = Document.objects.filter(id=doc_id).first()
            if document:
                document.delete()
                deleted_files.append(document.id)

    doc_result = {'total': len(deleted_files), 'result': deleted_files}
    return Response(doc_result)


@api_view(['POST'])
@permission_classes([
    IsAuthenticated,
    FunctionPermission([
        'readRepository'
    ]),
])
def refresh_connections(request):
    if not Repository.objects.filter(connector_id__in=[1]).exists():
        return Response(
            {'error': ['No repository found.']},
            status=status.HTTP_404_NOT_FOUND
        )
    # params = json.loads(request.body.decode('utf-8'))
    if cache.get('scan_running'):
        return Response({'total': 0, 'result': []}, status=status.HTTP_200_OK)
    else:
        # expiration time will be updated when total file count retrieved
        cache.set('scan_running', True, 60 * 5)
    update_connections_thread()
    doc_result = {'total': 0, 'result': []}
    return Response(doc_result)


def get_file_content(doc_id):
    try:
        document = Document.objects.filter(id=doc_id).first()
        content = document.content.strip()
        # return first 1000 character
        return content
    except Exception as ex:
        print(str(ex))
    return None


@api_view(['POST'])
@permission_classes([IsAuthenticated, ])
def get_document_content(request):
    try:
        doc_id = request.data.get('id')
        doc_content = get_file_content(doc_id)
        doc_result = {'result': doc_content}
        return Response(doc_result)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated, ])
def get_cached_status(request):
    in_progress = False
    status_name = request.data.get('status_name')
    if cache.get(status_name):
        logger.debug(f'{status_name} is already in progress')
        in_progress = True
    return Response({'status': in_progress}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([
    IsAuthenticated,
])
def search_elastic(request):
    search_key = request.data.get('key')
    print(search_key)
    documents = Document.objects.filter(content=search_key).all()
    serializer = DocumentSerializer(documents, many=True)
    doc_result = {'total': len(documents), 'result': serializer.data}
    return Response(doc_result)
