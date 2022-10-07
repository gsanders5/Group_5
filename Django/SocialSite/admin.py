from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . import models


# Register your models here.
@admin.register(models.Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['email', 'username', 'date_joined', 'last_login', 'is_admin', 'is_staff']
    search_fields = ['email', 'username']
    readonly_fields = ['id', 'date_joined', 'last_login']
    list_per_page = 100
    list_editable = []


@admin.register(models.FriendList)
class FriendListAdmin(admin.ModelAdmin):
    list_filter = ['user']
    list_display = ['user']
    search_fields = ['user']
    readonly_fields = ['user']

    class Meta:
        model = models.FriendList


@admin.register(models.FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_filter = ['sender', 'receiver']
    list_display = ['sender', 'receiver']
    search_fields = ['sender__email', 'sender__username', 'sender__id', 'receiver__email', 'receiver__username', 'receiver__id']

    class Meta:
        model = models.FriendRequest




