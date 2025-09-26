from django.contrib import admin
from .models import EmailTemplate, EmailUser
from django_summernote.admin import SummernoteModelAdmin


@admin.register(EmailTemplate)
class EmailTemplateAdmin(SummernoteModelAdmin):
    list_display = ("id", "title", "code")
    search_fields = ("title", "code")
    summernote_fields = ("content",)


@admin.register(EmailUser)
class EmailUserAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "template", "user", "sent", "created_at")
    search_fields = ("code", "user__email", "template__code")
    list_filter = ("code", "created_at")
