from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from jobs.models import AuditLogs
from jobs.jobs import ScheduleControl

schedule_control = ScheduleControl()


@api_view(['POST'])
@permission_classes([
    IsAuthenticated,
])
def start_logs_scheduler(request):
    try:
        schedule_control.start()
        audit_logs = AuditLogs.objects.values()
        log_result = {'result': audit_logs}
        return Response(log_result)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([
    IsAuthenticated,
])
def stop_logs_scheduler(request):
    try:
        schedule_control.stop()
        audit_logs = AuditLogs.objects.values()
        log_result = {'result': audit_logs}
        return Response(log_result)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
