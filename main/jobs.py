import time
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from django.db import connection

from django.db.models import Q
from main import vmoperations as vmo
from datetime import datetime, timedelta
from django.db import transaction

# scheduler = BackgroundScheduler()
# scheduler.add_jobstore(DjangoJobStore(), "default")
scheduler = BackgroundScheduler(timezone='UTC')




# @register_job(scheduler, "interval", minutes=1)
# def deleteprojectdocuments():
#     # from . import bosoperations as ent
#     print("deleteprojectdocuments  job started! " + str(datetime.now()))
#     try:
#         result = vmo.delete_vm('test1')
#     except Exception as e:
#         print(e)
#         EntegrasyonErros.objects.create(msg=e, methodname='deleteprojectdocuments')
#     finally:
#         print("deleteprojectdocuments  job finished! " + str(datetime.now()))

def start():
    try:
        # scheduler.add_jobstore(DjangoJobStore(),'default')
        register_events(scheduler)
        scheduler.start()
        print("Scheduler started!")
    except Exception as e:
        print(e)
