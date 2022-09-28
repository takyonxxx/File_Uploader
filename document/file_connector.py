import asyncio
import concurrent
import json
import math
import os
import socket
import threading
import time
from datetime import date, datetime
from logging import getLogger

from django.core.cache import cache
from impacket.smbconnection import SMBConnection
from smb.smb_constants import FILE_READ_DATA

from document.file_template import FileTemplate
from document.models import Document, RepositoryMetadata
from document.utils import get_file_uploader, read_configuration
from main.consumers import NotificationConsumer as ws


def convert_size(size_bytes):
    if size_bytes == 0:
        return '0B'
    size_name = ('B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return '%s %s' % (s, size_name[i])


class FileConnector(threading.Thread):
    __instance__ = None

    def __init__(self, con_id, repository, unc_path, frequency, start_date):

        if FileConnector.__instance__ is None:
            FileConnector.__instance__ = self

        threading.Thread.__init__(self)
        self.lock = threading.Lock()
        self._kill = threading.Event()
        self.loop = None
        self.loop_delay = 1
        self.last_update_time = time.time()
        self.first_start = True
        self.con_id = con_id
        self.print = getLogger().info

        self.repository = repository
        self.name = self.__class__.__name__
        # daily
        if int(frequency) == 1:
            self.period = 86400
        # weekly
        elif int(frequency) == 2:
            self.period = 7 * 86400
        # monthly
        elif int(frequency) == 3:
            self.period = 30 * 86400

        self.start_date = start_date

        self.id = id

        self.description = 'File System'
        self.unc_path = unc_path
        self.share_path = None
        self.remote_name = socket.gethostname()  # "repofilerserver"
        self.remote_ip = None
        self.remote_port = 445
        self.client_name = socket.gethostname()
        self.smb_client = None

        self.file_uploader = None
        self.paths = list()
        self.folders = list()
        self.doc_current_number = 0
        self.repo_doc_total_number = 0
        self.repo_doc_total_size = 0

        file_uploader = get_file_uploader()
        if file_uploader:
            self.file_uploader = file_uploader

        self.username = 'samba_user'
        self.password = ''
        self.distinguished_name = ''

    @staticmethod
    def get_instance():
        return FileConnector.__instance__

    def get_path_len(self):
        return len(self.paths)

    def connect(self):
        # smb://172.16.0.110/Ureticiler
        if '//' not in self.unc_path:
            self.print('Wrong UNC Path {}'.format(self.unc_path))
            return

        path_args = self.unc_path.split('//')
        path_args = path_args[1].split('/')
        if len([path_args[0]]) > 0:
            self.remote_ip = path_args[0]
        if len([path_args[1]]) > 0:
            self.share_path = path_args[1]

        try:
            self.smb_client = SMBConnection(self.remote_ip, self.remote_ip, sess_port=int(self.remote_port))
            self.smb_client.login(self.username, self.password, self.distinguished_name)

            self.print(f'File connection status for {self.remote_ip}:{self.remote_port}'
                       f' => {self.smb_client.getRemoteHost()}')
            ws.send_message({
                'text': f'File connection status for {self.remote_ip}:{self.remote_port}'
                        f' => {self.smb_client.getRemoteHost()}',
                'details': {}
            })
        except Exception as e:
            self.smb_client = None
            self.print('Error smb_client connect : ' + str(e))

        if self.smb_client and self.file_uploader and self.file_uploader.is_connected():
            message = (f'File Connector connected to : {self.remote_ip} '
                       f'collection: {self.repository} path: {self.share_path}')
            self.print(message)
            ws.send_message({
                'text': message,
                'details': {},
            })
            return True
        return False

    def is_connected(self):
        if self.smb_client and self.file_uploader and self.file_uploader.is_connected():
            return True
        return False

    def send_file(self, file):
        if self.file_uploader and self.file_uploader.is_connected():
            self.file_uploader.add(file)

    def send_document_async(self, file_template):
        def make_request(_file_template):
            return self.send_file(_file_template)

        # return make_request(file_template)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(make_request, file_template)
            return_value = future.result()
            return return_value

    def delete_file(self, doc_id):
        if self.file_uploader and self.file_uploader.is_connected():
            self.file_uploader.delete_file(doc_id)

    def delete_document_async(self, doc_id):
        def make_request(_doc_id):
            return self.delete_file(_doc_id)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(make_request, doc_id)
            return_value = future.result()
            return return_value

    def get_documents_count(self, share_path, top=u'*'):
        dirs = list()

        if not isinstance(self.smb_client, SMBConnection):
            raise TypeError('FileConnector : SMBConnection required')

        try:
            files = self.smb_client.listPath(share_path, top)

            for f in files:
                f_name = f.get_longname()

                if f_name in [u'.', u'..']:
                    continue

                if f.is_directory():
                    folder_name = f.get_longname()
                    dirs.append(folder_name)
                else:

                    if f_name.startswith('.'):
                        continue

                    self.repo_doc_total_number += 1
                    self.repo_doc_total_size += f.get_filesize()

        except Exception as e:
            self.print('Error get_documents_count : ' + str(e))

        for folder in dirs:
            top = top.replace('*', '')
            if len(top) == 0:
                new_path = folder + '/*'
            else:
                new_path = top + folder + '/*'

            self.get_documents_count(share_path, new_path)

    async def get_documents(self, share_path, top=u'*'):

        dirs = list()

        if not isinstance(self.smb_client, SMBConnection):
            raise TypeError('FileConnector : SMBConnection required')

        files = self.smb_client.listPath(share_path, top)
        file_tree = self.smb_client.connectTree(share_path)
        for f in files:
            f_name = str(f.get_longname())

            if f_name in [u'.', u'..']:
                continue

            if f.is_directory():
                folder_name = f.get_longname()
                dirs.append(folder_name)

                folder_path = share_path + '/' + top
                folder_path = folder_path[:-2]
                if folder_path not in self.folders:
                    self.folders.append(folder_path)
            else:

                if f_name.startswith('.'):
                    continue

                meta_data = {'file_name': f_name,
                             'file_size': f.get_filesize(),
                             'file_source': self.__class__.__name__,
                             'last_access_time': f.get_atime_epoch(),
                             'create_time': f.get_ctime_epoch()}

                # file_only_name, file_extension = os.path.splitext(f_name)

                file_dir_path = share_path + '/' + top
                file_dir_path = file_dir_path[:-2]
                file_short_path = file_dir_path + '/' + f_name
                file_name = top[:-2] + '/' + f_name
                try:
                    remote_file = self.smb_client.openFile(file_tree, file_name, desiredAccess=FILE_READ_DATA)
                    file_content = self.smb_client.readFile(file_tree, remote_file)
                    self.smb_client.closeFile(file_tree, remote_file)
                except Exception as e:
                    self.print('Error smb open file: {} {}'.format(f_name, str(e)))
                    continue

                self.print(f'File {f_name} retrieved: {meta_data}(attr), {f.get_filesize()}(size)')

                self.doc_current_number += 1

                file_template = FileTemplate(
                    file_repository=self.repository,
                    file_description=self.description,
                    file_path=file_short_path,
                    file_dir_path=file_dir_path,
                    file_path_length=self.repo_doc_total_number,
                    content=file_content,
                    number=self.doc_current_number,
                    metadata=meta_data,
                )

                if file_short_path not in self.paths:
                    self.print(f'appending paths {file_short_path}')
                self.paths.append(file_short_path)
                self.send_document_async(file_template)

        for folder in dirs:
            top = top.replace('*', '')
            if len(top) == 0:
                new_path = folder + '/*'
            else:
                new_path = top + folder + '/*'

            await asyncio.gather(self.get_documents(share_path, new_path))

    async def check_documents_async(self):

        self.print('Checking documents asynchronously...')
        if not self.is_connected():
            self.print('Unexpected: File connector is not connected')
            return
        try:
            self.paths.clear()
            self.folders.clear()
            self.repo_doc_total_number = 0
            self.doc_current_number = 0

            # get total doc number
            self.get_documents_count(self.share_path)

            cache.set('scan_running', True, int(self.repo_doc_total_number / 3))
            self.print(f'Expiration of -scan_running- is set to {int(self.repo_doc_total_number / 3)}')

            # get docs with content and metadata
            await asyncio.gather(self.get_documents(self.share_path))

            if self.repository:
                repository_meta_last = RepositoryMetadata.objects.filter(repository=self.repository).last()
                if repository_meta_last:
                    old_paths = repository_meta_last.schema
                    json_dec = json.decoder.JSONDecoder()
                    old_path_list = json_dec.decode(old_paths)
                    for path in old_path_list:
                        if path not in self.paths:
                            doc_by_path = Document.objects.filter(path=path).first()
                            if doc_by_path:
                                doc_id = str(doc_by_path.id)
                                self.delete_document_async(doc_id)
                                self.print('File {} removed from path: {}'
                                           .format(doc_by_path.name, self.share_path))
                if len(self.paths) > 0:
                    metadata = RepositoryMetadata(
                        repository=self.repository,
                        schema=json.dumps(self.paths),
                        folders=json.dumps(self.folders),
                        created=datetime.utcnow()
                    )
                    metadata.save()

        except Exception as e:
            self.print(str(e))

        self.print('Completed async check...')

    def run(self):
        if not self.is_connected():
            self.connect()

        while True:
            is_killed = self._kill.wait(self.loop_delay)
            if is_killed:
                self.print(f'{self.__class__.__name__} killed')
                ws.send_message({'text': 'Old thread killed..', 'details': {}})
                self.smb_client = None
                self.file_uploader = None
                break

            date_start = datetime.strptime(self.start_date, '%Y-%m-%dT%H:%M:%S%z')
            delta = date_start.date() - date.today()
            if delta.days > 0:
                continue

            if (time.time() - self.last_update_time) > self.period or self.first_start:
                self.lock.acquire()
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)
                self.loop.run_until_complete(self.check_documents_async())
                self.loop.close()
                self.lock.release()
                self.last_update_time = time.time()
                self.first_start = False

    def kill(self):
        self._kill.set()

    def __eq__(self, other):
        return (self.name,) == (other.name,)

    def __hash__(self):
        return hash((self.name,))

    def __str__(self):
        return self.name
