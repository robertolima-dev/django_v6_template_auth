from django.utils import timezone

from apps.event_sync.managers.sync_data import SyncData
from apps.event_sync.models import EventSync


class ConsumerMsg:
    def sync(self, sync_data: SyncData) -> None:

        event_id = sync_data.obj_data.get('event_id')
        instance = EventSync.objects.filter(
            id=event_id
        ).first()

        instance.received = timezone.now()

        try:
            if sync_data.obj_type == "test_event_sync":
                # TODO: Implement the logic to handle the test event sync
                instance.processed = timezone.now()
                instance.save()

        except Exception as e:
            instance.log = str(e)
            instance.save()
