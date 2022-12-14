from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.files.storage import default_storage
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


def get_profile_image_filepath(self, filename):
    return 'profile_images/' + str(self.pk) + '/profile_image.png'


def get_default_profile_image():
    return "media/defaultProfileImage.png"


def get_default_post_image():
    return "media/defaultPostImage.png"


def get_profile_image_directory(self, filename):
    return "profile_images/" + filename



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
    if instance.profile_image is None:
        instance.profile_image.url = "media/defaultProfileImage.png"


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
    poster = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='post_poster', null=True, blank=True)
    num_of_likes = models.IntegerField(default='0')
    text_content = models.TextField(blank=True, null=True)
    image = models.ImageField(null=True, blank=True, upload_to=get_profile_image_directory, default=get_default_post_image)
    created_at = models.DateTimeField(auto_now_add=True)
    is_image = models.BooleanField(default=False)
    is_shared_post = models.BooleanField(default=False)
    shared_post = models.OneToOneField('Post', blank=True, null=True, on_delete=models.CASCADE)
    usersWhoLiked = models.ManyToManyField('Account', blank=True, related_name='users_who_liked')
    usersWhoShared = models.ManyToManyField('Account', blank=True, related_name='users_who_shared')
    tagged_users = models.CharField(max_length=255, blank=True, null=True)
    tagged_location = models.CharField(max_length=255, blank=True, null=True)

    def like_post(self, account: Account):
        if account not in self.usersWhoLiked.all():
            self.usersWhoLiked.add(account)
        self.num_of_likes = self.usersWhoLiked.count()
        self.save()

        return self.num_of_likes

    def unlike_post(self, account: Account):
        if account in self.usersWhoLiked.all():
            self.usersWhoLiked.remove(account)
        self.num_of_likes = self.usersWhoLiked.count()
        self.save()

        return self.num_of_likes

    def share_post(self, account: Account):
        account_post_list = PostList.objects.get(user=account)
        if account_post_list:
            new_post = Post()
            new_post.is_shared_post = True
            new_post.shared_post = self
            new_post.poster = account
            self.usersWhoShared.add(account)
            new_post.save()
            self.save()
            account_post_list.add_post(new_post)

    def __str__(self):
        return "PostId: " + str(self.id) + " PostedBy: " + str(self.userId)


@receiver(post_save, sender=Post)
def post_save(sender, instance, **kwargs):
    CommentList.objects.get_or_create(post=instance)


class PostList(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='poster')
    posts = models.ManyToManyField('Post', blank=True, related_name='posts')

    def add_post(self, post: Post):
        if post not in self.posts.all():
            self.posts.add(post)

    def remove_post(self, post: Post):
        if post in self.posts.all():
            self.posts.remove(post)

    def __str__(self):
        return "UserId: " + str(self.user.id) + " PostListId: " + str(self.id)


class Comment(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="commenter", blank=True, null=True)
    text_content = models.TextField()
    createdAt = models.DateTimeField(auto_now_add=True)


class CommentList(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name='postComment')
    comments = models.ManyToManyField('Comment', related_name='comments', blank=True)

    def add_comment(self, comment: Comment):
        if comment not in self.comments.all():
            self.comments.add(comment)

    def remove_comment(self, comment: Comment):
        if comment in self.comments.all():
            self.comments.remove(comment)






