from django.contrib import admin
from . import models


# Register your models here.


@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'firstName', 'lastName', 'email']
    list_per_page = 100
    list_editable = []


# @admin.register(models.FriendLink)
# class FriendLinkAdmin(admin.ModelAdmin):
# list_display = ['id', 'senderId', 'recipientId']


# admin.site.register(models.Profile)
admin.site.register(models.Post)
admin.site.register(models.FriendList)
