import ctypes
import logging
import traceback
from datetime import date
from threading import Thread

from django.core.cache import cache

from connection.serializers import RepositorySerializer
from document.file_connector import FileConnector
from document.models import Repository
from document.utils import get_file_uploader
from main.consumers import NotificationConsumer as ws

connector_list = []
logger = logging.getLogger(__name__)


def stop_connectors():
    logger.debug(f'Total instance count : {len(connector_list)}')
    get_file_uploader().kill()
    while len(connector_list) > 0:
        for t_instance in connector_list:
            try:
                t_instance.kill()
                t_instance.join()
                connector_list.remove(t_instance)
            except Exception as ex:
                logger.debug(str(ex))
                logger.debug(traceback.format_exc())
                return False
    return True


def update_connections_thread():
    thread = Thread(target=update_connections)
    thread.start()
    thread.join()


def terminate_thread(thread):
    if not thread.isAlive():
        return

    exc = ctypes.py_object(SystemExit)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_long(thread.ident), exc)
    if res == 0:
        raise ValueError('nonexistent thread id')
    elif res > 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident, None)
        raise SystemError('PyThreadState_SetAsyncExc failed')


def update_connections():
    temp_list = []

    file_uploader = get_file_uploader()
    if not file_uploader:
        if cache.get('scan_running'):
            cache.delete('scan_running')
        return

    stop_connectors()
    connector_list.clear()

    repos = Repository.objects.filter(connector_id__in=[1, 2, 3])
    serializer = RepositorySerializer(repos, many=True)
    connections = serializer.data

    for connection in connections:
        dict_connection = dict(connection)
        con_id = dict_connection['connector']
        start_date = dict_connection['start_date']
        # con_info = Connector.objects.filter(id=con_id).first()
        frequency = dict_connection['frequency']
        name = dict_connection['name']
        fields = dict_connection['fields']
        repository = Repository.objects.filter(name=name).first()
        if not repository:
            continue

        date_start = repository.start_date
        delta = date_start.date() - date.today()
        if delta.days > 0:
            continue

        if con_id == 1:
            ws.send_message({
                'text': f'Repository {name} will be uploaded.',
                'details': {}
            })
            for field in fields:
                field = dict(field)
                connection_property = dict(field['connection_property'])
                if connection_property['name'] == 'UNC Path':
                    unc_path = field['value']
                    connector_t = FileConnector(con_id, repository, unc_path, frequency, start_date)
                    if connector_t not in temp_list:
                        cache.set('fileConnectorRunning', True)
                        temp_list.append(connector_t)

    for t_instance in temp_list:
        try:
            if t_instance not in connector_list:
                logger.debug('START T_INSTANCE')
                t_instance.start()
                connector_list.append(t_instance)
        except Exception as ex:
            logger.debug(str(ex))
