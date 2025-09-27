from django.utils import timezone

from apps.event_sync.models import EventSync
from common.sqs.sqs_sync import SqSManager


class ProducerMsg:

    def __init__(self, apps, obj_type, obj_data, obj_cmd):
        self.apps = apps
        self.obj_type = obj_type
        self.obj_data = obj_data
        self.obj_cmd = obj_cmd

    def handle_msg_sync(self, ):

        instance = EventSync.objects.create(
            apps=self.apps,
            obj_type=self.obj_type,
            obj_data=self.obj_data,
            obj_cmd=self.obj_cmd,
        )

        data = self.obj_data
        data['event_id'] = instance.id

        msg = {
            "apps": self.apps,
            "data": {
                "obj_type": self.obj_type,
                "obj_data": data,
                "obj_cmd": self.obj_cmd
            },
            "timestamp": timezone.now().timestamp()
        }

        self.send_msg_to_sqs(
            msg=msg,
            instance=instance
        )

    def send_msg_to_sqs(self, msg, instance, ):

        try:
            SqSManager.send(msg=msg)
            instance.sent = timezone.now()
            instance.save()
        except Exception as e:
            instance.log = str(e)
            instance.save()
