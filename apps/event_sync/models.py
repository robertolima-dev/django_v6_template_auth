from django.db import models
from api_core.base_model import BaseModel


class EventSync(BaseModel):
    apps = models.JSONField(null=True)
    obj_type = models.CharField(max_length=120, null=True)
    obj_data = models.JSONField(null=True)
    obj_cmd = models.CharField(max_length=20, null=True)
    sent = models.DateTimeField(null=True)
    received = models.DateTimeField(null=True)
    processed = models.DateTimeField(null=True)
    log = models.TextField(null=True)

    class Meta:
        verbose_name = "Event Sync"
        verbose_name_plural = "Events Sync"

    def __str__(self) -> str:
        return str(self.obj_type)
