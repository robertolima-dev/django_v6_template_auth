from django.contrib import admin

from .models import EventSync


@admin.register(EventSync)
class EventSyncAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'obj_type', 'obj_cmd', 'sent', 'received', 'processed', 'created_at', 'updated_at'  # noqa: E501
    )
    list_display_links = ('id', 'obj_type')
    search_fields = ('obj_type', 'obj_cmd', 'log')
    list_filter = ('obj_type', 'obj_cmd', 'created_at', 'sent', 'processed')
    readonly_fields = ('created_at', 'updated_at', 'sent', 'received', 'processed')  # noqa: E501
    fieldsets = (
        ("Informações do Evento", {
            'fields': ('obj_type', 'obj_cmd', 'apps', 'obj_data')
        }),
        ("Status do Evento", {
            'fields': ('sent', 'received', 'processed', 'log')
        }),
        ("Datas", {
            'fields': ('created_at', 'updated_at')
        }),
    )
    list_per_page = 25
