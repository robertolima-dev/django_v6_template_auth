from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User, UserToken


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email", "phone", "gender", "date_of_birth")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2", "first_name", "last_name", "email", "phone", "gender", "date_of_birth"),
            },
        ),
    )
    list_display = ("username", "email", "first_name", "last_name", "is_staff")
    search_fields = ("username", "first_name", "last_name", "email")
    ordering = ("username",)

from django.contrib import admin


@admin.register(UserToken)
class UserTokenAdmin(admin.ModelAdmin):
    list_display = ("token", "user", "token_type", "expired_at")
    list_filter = ("token_type",)
    search_fields = ("token", "user__username", "user__email")
