# -*- coding: utf-8 -*-
import asyncio
import concurrent
import json
import os
import queue
import threading
import time
from datetime import datetime
from logging import getLogger

from django.core.cache import cache

from document.models import Document
from main.consumers import NotificationConsumer as ws

os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'true'


class FileUploader(threading.Thread):
    __instance__ = None

    def __init__(self):

        if FileUploader.__instance__ is None:
            FileUploader.__instance__ = self
        else:
            raise Exception('You cannot create another SingletonGovt class')

        threading.Thread.__init__(self)
        self.print = getLogger().info
        self.lock = threading.Lock()
        self._STOP = False
        self.loop = None
        self.loop_delay = 0.1
        self.q = queue.Queue()
        self.last_processed_item = 0
        self._kill = threading.Event()
        self.start()

    @staticmethod
    def get_instance():
        if not FileUploader.__instance__:
            FileUploader()
        return FileUploader.__instance__

    def is_connected(self):
        if FileUploader.__instance__:
            return True
        return False

    def delete_file(self, doc_id):
        document = Document.objects.filter(id=doc_id).first()
        if document:
            document.delete()

    def add_document(self, file):

        file_content = file.content
        # JSON encoder fix requests unicode error
        if isinstance(file_content, str):
            file_content = json.dumps(file_content)

        if len(file_content) == 0:
            return

        progress_percentage = round(file.number * 100 / file.file_path_length, 2)
        if progress_percentage == 100:
            uploaded_file_count = Document.objects.filter(repository_id=file.file_repository.id).count()
            total_file_count = file.file_path_length
            final_status = ''

            if file.file_repository.connector_id == 1:
                final_status = f'{uploaded_file_count} of {total_file_count} files scanned successfully..'
                cache.delete('fileConnectorRunning')

            if cache.get('fileConnectorRunning') is None:
                cache.delete('scan_running')

            if file.number == file.file_path_length and file.file_path_length == self.last_processed_item + 1:
                self.last_processed_item += 1
                ws.send_message({
                    'finalStatus': final_status,
                    'details': {'progress_bar_percentage': progress_percentage}
                })

        elif progress_percentage < 100:
            # if one repository completed but the other one is still running,
            # set cache again to show the processing still continues
            cache.set('scan_running', True, 60 * 5)
            self.last_processed_item = file.number

        last_access_time = (datetime.fromtimestamp(file.metadata.last_access_time)
                            if file.metadata.last_access_time
                            else datetime.utcnow())
        created = (datetime.fromtimestamp(file.metadata.create_time)
                   if file.metadata.create_time
                   else datetime.utcnow())
        file_name = file.metadata.file_name or file.file_path
        file_size = file.metadata.file_size or 0

        file_changed = False
        file_exists = Document.objects.filter(path=file.file_path, repository=file.file_repository).exists()

        if file_exists:
            document = Document.objects.filter(path=file.file_path, repository=file.file_repository).get()
            if document.size != file.metadata.file_size:
                document.size = file.metadata.file_size
                file_changed = True
        else:
            document = Document(
                source=file.metadata.file_source,
                repository=file.file_repository,
                name=file_name,
                path=file.file_path,
                dir_path=file.file_dir_path,
                path_len=file.file_path_length,
                size=file_size,
                content=file_content,
                last_access_time=last_access_time,
                created=created
            )

        if not file_exists or file_changed:
            try:
                document.save()
            except Exception as e:
                self.print('Error file_uploader document.save(): {} {}'.format(document.name, str(e)))
                return False

            self.print(f'{document.path} uploaded to {document.repository.name} '
                       f' {str(file.number)}/{str(file.file_path_length)}/{file.file_path}')
            ws.send_message({
                'text': f'{document.path} uploaded to {document.repository.name}',
                'details': {
                    'progress_bar_percentage': progress_percentage,
                    'filename': document.name,
                    'file_path': file.file_path,
                    'file_repo': file.file_repository.name,
                    'current_file': file.number,
                    'total_files': file.file_path_length
                }
            })
            return True
        else:
            self.print(f'No changes detected for {document.path} in {document.repository.name}')
            ws.send_message({
                'text': f'No changes detected for {document.path} in {document.repository.name}',
                'details': {
                    'progress_bar_percentage': progress_percentage,
                    'filename': document.name,
                    'file_path': file.file_path,
                    'file_repo': file.file_repository.name,
                    'current_file': file.number,
                    'total_files': file.file_path_length
                }
            })
            return False

    def send_item_async(self, item):
        def make_request(_item):
            return self.add_document(_item)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(make_request, item)
            return_value = future.result()
            return return_value

    def add(self, item):
        if item not in self.q.queue:
            self.q.put(item)

    async def upload_queue_async(self):
        if not self.q.empty():
            try:
                item = self.q.get_nowait()
                if item is None:
                    return
                try:
                    self.send_item_async(item)
                finally:
                    self.q.task_done()
            except queue.Empty:
                pass

    def run(self):
        while True:
            if self._STOP:
                break

            self.lock.acquire()
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(self.upload_queue_async())
            self.loop.close()
            self.lock.release()

            time.sleep(self.loop_delay)

    def join(self, timeout=0.1):
        self._STOP = True
        self.q.join()
        super().join(timeout=timeout)

    def kill(self):
        self._kill.set()
        with self.q.mutex:
            self.q.queue.clear()
