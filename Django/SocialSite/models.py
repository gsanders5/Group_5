from django.db import models


# Create your models here.
# Relationship types for Sharing/Liking Posts
# Look at making indexes

class Profile(models.Model):
    firstName = models.CharField(max_length=255)
    lastName = models.CharField(max_length=255)
    username = models.CharField(max_length=255, default='%s_%s' % (firstName, lastName))
    email = models.EmailField()
    phoneNumber = models.CharField(max_length=255)
    bio = models.TextField()
    isPrivate = models.BooleanField(default='True')
    isAdmin = models.BooleanField(default='False')
    friendsList = models.ForeignKey('FriendList', on_delete=models.CASCADE)
    postList = models.ForeignKey('PostList', on_delete=models.CASCADE)

    def __str__(self):
        return self.firstName + " " + self.lastName

    class Meta:
        ordering = ["id"]


# Friend List implementation: https://www.youtube.com/watch?v=hyJO4mkdwuM&list=PLgCYzUzKIBE9KUJZJUmnDFYQfVyXYjX6r&index=15
class FriendList(models.Model):
    user = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='user')
    friends = models.ManyToManyField(Profile, blank=True, related_name='friends')


class PostList(models.Model):
    user = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='poster')
    posts = models.ManyToManyField('Post', blank=True, related_name='posts')


class Post(models.Model):
    userId = models.IntegerField()
    numOfLikes = models.IntegerField(default='0')
    content = models.TextField()
    # image = models.ImageField() -> need to handle storage to implement
    createdAt = models.DateTimeField()


