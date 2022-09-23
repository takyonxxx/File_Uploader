from django.core.paginator import InvalidPage
from django.shortcuts import get_object_or_404
from django.urls import path
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, pagination
from rest_framework.exceptions import APIException, NotFound
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet


class CustomPagination(pagination.PageNumberPagination):
    page_size_query_param = 'itemsPerPage'
    page = None
    request = None

    def get_paginated_response(self, data):
        return Response({
            'total': self.page.paginator.count,
            'result': data
        })

    def paginate_queryset(self, queryset, request, view=None):
        page_size = request.data.get(self.page_size_query_param, self.page_size)

        if not page_size:
            page_size = (queryset.count() if queryset.count() != 0 else 1)
        paginator = self.django_paginator_class(queryset, page_size)
        page_number = request.data.get(self.page_query_param, 1)
        if page_number in self.last_page_strings:
            page_number = paginator.num_pages

        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            msg = self.invalid_page_message.format(
                page_number=page_number, message=str(exc)
            )
            raise NotFound(msg)

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request
        return list(self.page)


class CustomSearchFilter(filters.SearchFilter):
    def get_search_terms(self, request):
        params = request.data.get(self.search_param, '')
        if params is None:
            params = ''
        params = params.replace('\x00', '')  # strip null characters
        params = params.replace(',', ' ')
        return params.split()


class CustomDjangoFilterBackend(DjangoFilterBackend):
    def get_filterset_kwargs(self, request, queryset, view):
        return {
            'data': request.data,
            'queryset': queryset,
            'request': request,
        }


class BaseViewSet(ModelViewSet):
    pagination_class = CustomPagination
    default_filters = [CustomSearchFilter, CustomDjangoFilterBackend]

    def get_serializer_class(self):
        read_serializer_class = getattr(self, 'read_serializer_class', None)
        if read_serializer_class and self.action in ['list', 'retrieve']:
            return read_serializer_class
        else:
            return self.serializer_class

    @classmethod
    def use_for(cls, method):
        return cls.as_view({'post': method})

    def get_object(self):
        queryset = self.get_queryset()
        data = self.request.data
        _id = data.get('id')
        if _id is None:
            raise APIException('You should pass id value for retrieve object.')

        obj = get_object_or_404(queryset, pk=_id)
        self.check_object_permissions(self.request, obj)
        return obj

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends + self.default_filters):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def bulk_update(self, request, *args, **kwargs):
        data = request.data
        ids = []
        queryset = self.get_queryset()
        for datum in data:
            _id = datum.get('id')
            if _id is not None:
                ids.append(_id)
                obj = get_object_or_404(queryset, pk=_id)
                serializer = self.get_serializer(obj, data=datum)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
        instances = queryset.filter(id__in=ids)
        serializer = self.get_serializer(instances, many=True)
        return Response(serializer.data)


def create_view_paths(path_name, view):
    return [
        path('get{0}s/'.format(path_name), view.as_view({'post': 'list'})),
        path('get{0}ById/'.format(path_name), view.as_view({'post': 'retrieve'})),
        path('create{0}/'.format(path_name), view.as_view({'post': 'create'})),
        path('update{0}/'.format(path_name), view.as_view({'post': 'update'})),
        path('delete{0}/'.format(path_name), view.as_view({'post': 'destroy'})),
        path('bulkCreate{0}/'.format(path_name), view.as_view({'post': 'bulk_create'})),
        path('bulkUpdate{0}/'.format(path_name), view.as_view({'post': 'bulk_update'})),
    ]
