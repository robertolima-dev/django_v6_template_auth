from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.event_sync.api.serializers import AuthSyncSerializer
from apps.event_sync.managers.consumer_msg import ConsumerMsg
from apps.event_sync.managers.sync_data import SyncData
from common.sqs.sqs_permission import IsSqsAuthenticated


class EventSyncApiView(APIView):
    http_method_names = ['post', ]
    serializer_class = AuthSyncSerializer
    permission_classes = (IsSqsAuthenticated,)
    authentication_classes = ()

    def post(self, request, ):

        serializer = AuthSyncSerializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)

        try:
            sync_manager = ConsumerMsg()
            sync_manager.sync(SyncData(**serializer.validated_data))
        except Exception as e:
            return Response(str(e), status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
