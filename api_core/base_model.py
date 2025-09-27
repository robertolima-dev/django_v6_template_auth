from django.db import models


class BaseModel(models.Model):
    updated_at = models.DateTimeField(auto_now=True, db_index=True, null=True, )  # noqa: E501
    created_at = models.DateTimeField(auto_now_add=True, null=True, )  # noqa: E501
    deleted_at = models.DateTimeField(null=True, blank=True)  # noqa: E501

    class Meta:
        abstract = True
