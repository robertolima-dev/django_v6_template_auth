from rest_framework import serializers


class AuthSyncSerializer(serializers.Serializer):
    obj_type = serializers.CharField(required=True)
    obj_data = serializers.JSONField(required=True)
    obj_cmd = serializers.ChoiceField(
        choices=(("put", "put"), ("delete", "delete")), required=True
    )
