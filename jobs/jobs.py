import json
from datetime import datetime
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc
from jobs.models import AuditLogs


class ScheduleControl:

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.configure(timezone=utc)

    def start(self):
        if self.scheduler is None:
            self.scheduler = BackgroundScheduler()

        self.scheduler.add_job(self.read_datas, "interval", seconds=5)
        self.scheduler.start()
        print("Scheduler started!")

    def stop(self):
        try:
            if self.scheduler is not None:
                self.scheduler.remove_all_jobs()
                self.scheduler.shutdown(wait=False)
                self.scheduler = None
                print("Scheduler stopped!")
        except Exception as e:
            print(e)

    def read_datas(self):
        url = "https://giris.iys.org.tr/auth/realms/master/protocol/openid-connect/token"

        payload = 'username=softtech&password=QY20Ru9715568K1HkH6e&client_id=security-admin-console&client_secret=tLW8x3fd1B5L5BbZUakecQgAvAktA2SeGTfzsRmfxuHlJJFbp92txP6WPvBGOqIKuAHjXIzefkBlA4JLNHEoUUHBmqccz3Wa&grant_type=password&scope=openid'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        j_response = json.loads(response.text)
        token = j_response['access_token']
        self.get_audit_logs(token)

    def get_audit_logs(self, token):

        url = "https://giris.iys.org.tr/auth/admin/realms/master/clients/c8b3ffd5-afa2-49d7-8a07-6a4088d88b44/user-sessions"

        payload = {}
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer' + ' ' + str(token)
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        response_array = json.loads(response.text)
        for log in response_array:
            clients = log['clients']
            log_id = log['id']
            ip_address = log['ipAddress']
            last_access = log['lastAccess']
            log_start = log['start']
            user_id = log['userId']
            username = log['username']
            last_access = datetime.fromtimestamp(last_access / 1e3)
            log_start = datetime.fromtimestamp(log_start / 1e3)
            # print(log_start.strftime('%Y-%m-%d %H:%M:%S'), last_access.strftime('%Y-%m-%d %H:%M:%S'))

            try:
                AuditLogs.objects.create(
                    id=log_id,
                    clients=clients,
                    ip_address=ip_address,
                    last_access=last_access,
                    start=log_start,
                    user_id=user_id,
                    username=username
                )
            except Exception as ex:
                pass
