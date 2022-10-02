from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


# Create your models here.
# Relationship types for Sharing/Liking Posts
# Look at making indexes

class MyAccountManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError("Users must have an email address")
        if not username:
            raise ValueError("Users must have a username")
        user = self.model(
            email=self.normalize_email(email),
            username=username
        )
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password
        )
        user.is_admin = True
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self.db)
        return user


def get_profile_image_filepath(self):
    return f'profile_images/{self.pk}/{"profile_image.png"}'


def get_default_profile_image():
    return "media/defaultProfileImage.png"


class Account(AbstractBaseUser):
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    username = models.CharField(max_length=255, unique=True)
    date_joined = models.DateTimeField(verbose_name="date joined", auto_now_add=True)
    last_login = models.DateTimeField(verbose_name="last login", auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    profile_image = models.ImageField(max_length=255, upload_to=get_profile_image_filepath, null=True, blank=True, default=get_default_profile_image)
    hide_email = models.BooleanField(default=True)
    isPrivate = models.BooleanField(default='True')

    friendsList = models.ForeignKey('FriendList', on_delete=models.CASCADE, null=True)
    postList = models.ForeignKey('PostList', on_delete=models.CASCADE, null=True)

    objects = MyAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    def get_profile_image_filename(self):
        return str(self.profile_image)[str(self.profile_image).index(f'profile_images/{self.pk}/'):]


# Friend List implementation: https://www.youtube.com/watch?v=hyJO4mkdwuM&list=PLgCYzUzKIBE9KUJZJUmnDFYQfVyXYjX6r&index=15

class FriendList(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='user')
    friends = models.ManyToManyField(Account, blank=True, related_name='friends')

    def add_friend(self, account):
        # add friend
        if account not in self.friends:
            self.friends.add(account)

    def remove_friend(self, account):
        # remove friend
        if account in self.friends:
            self.friends.remove(account)

    # Handle requests

    def __str__(self):
        return "UserId: " + str(self.user.id) + " FriendsListId: " + str(self.id)


class Post(models.Model):
    userId = models.IntegerField()
    numOfLikes = models.IntegerField(default='0')
    content = models.TextField()
    # image = models.ImageField() -> need to handle storage to implement
    createdAt = models.DateTimeField()
    usersWhoLiked = models.ManyToManyField('Account', blank=True, related_name='users_who_liked')

    def __str__(self):
        return "PostId: " + str(self.id) + " PostedBy: " + str(self.userId)


class PostList(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='poster')
    posts = models.ManyToManyField('Post', blank=True, related_name='posts')

    def add_post(self, post: Post):
        if post not in self.posts:
            self.posts.add(post)

    def remove_post(self, post: Post):
        if post in self.posts:
            self.posts.remove(post)

    def __str__(self):
        return "UserId: " + str(self.user.id) + " PostListId: " + str(self.id)
