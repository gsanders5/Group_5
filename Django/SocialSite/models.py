from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone


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
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
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


@receiver(post_save, sender=Account)
def user_save(sender, instance, **kwargs):
    FriendList.objects.get_or_create(user=instance)
    PostList.objects.get_or_create(user=instance)


class FriendList(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user')
    friends = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='friends')

    def add_friend(self, account):
        # add friend
        if account not in self.friends.all():
            self.friends.add(account)
            self.save()

    def remove_friend(self, account):
        # remove friend
        if account in self.friends.all():
            self.friends.remove(account)
            self.save()

    def unfriend(self, removee):
        remover_friends_list = self
        remover_friends_list.remove_friend(removee)
        friends_list = FriendList.objects.get(user=removee)
        friends_list.remove_friend(self.user)

    def is_mutual_friend(self, friend):
        if friend in self.friends.all():
            return True
        return False

    def __str__(self):
        return "UserId: " + str(self.user.id) + " FriendsListId: " + str(self.id)


class FriendRequest(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sender")
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="receiver")
    is_active = models.BooleanField(blank=True, null=False, default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sender.username

    def accept(self):
        receiver_friend_list = FriendList.objects.get(user=self.receiver)
        if receiver_friend_list:
            sender_friend_list = FriendList.objects.get(user=self.sender)
            if sender_friend_list:
                receiver_friend_list.add_friend(self.sender)
                sender_friend_list.add_friend(self.receiver)
                self.is_active = False
                self.save()

    def decline(self):
        self.is_active = False
        self.save()

    def cancel(self):
        self.is_active = False
        self.save()


class Post(models.Model):
    numOfLikes = models.IntegerField(default='0')
    description = models.TextField()
    image = models.ImageField(null=True, blank=True)
    createdAt = models.DateTimeField()
    # usersWhoLiked = models.ManyToManyField('Account', blank=True, related_name='users_who_liked')

    def __str__(self):
        return "PostId: " + str(self.id) + " PostedBy: " + str(self.userId)


@receiver(post_save, sender=Post)
def post_save(sender, instance, **kwargs):
    PostList.objects.get_or_create(post=instance)


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


class Comment(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='commenter')
    content = models.TextField()
    createdAt = models.DateTimeField(auto_now_add=True)


class CommentList(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name='postComment')
    comments = models.OneToOneField(Comment, on_delete=models.CASCADE, related_name='comments')





