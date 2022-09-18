
import django.utils.timezone
from django.db import models


# Create your models here.
# Relationship types for Sharing/Liking Posts
# Look at making indexes

class Profile(models.Model):
    firstName = models.CharField(max_length=255)
    lastName = models.CharField(max_length=255)
    email = models.EmailField()
    phoneNumber = models.CharField(max_length=255)
    bio = models.TextField()
    isPrivate = models.BooleanField(default='True')
    isAdmin = models.BooleanField(default='False')


class Post(models.Model):
    userId = models.IntegerField()
    numOfLikes = models.IntegerField(default='0')
    # image = models.ImageField() -> need to handle storage to implement
    createdAt = models.DateTimeField()


class FriendLink(models.Model):
    senderId = models.IntegerField()
    recipientId = models.IntegerField()

    STATUS_PENDING = 1
    STATUS_ACCEPTED = 2
    STATUS_REJECTED = 3
    STATUS_CHOICES = [
        (STATUS_PENDING, "PENDING"),
        (STATUS_ACCEPTED, "ACCEPTED"),
        (STATUS_REJECTED, "REJECTED"),
    ]
    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_PENDING)

