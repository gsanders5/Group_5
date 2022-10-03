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


# @admin.register(models.FriendLink)
# class FriendLinkAdmin(admin.ModelAdmin):
# list_display = ['id', 'senderId', 'recipientId']


# admin.site.register(models.Profile)
admin.site.register(models.Post)
admin.site.register(models.FriendList)
admin.site.register(models.PostList)
