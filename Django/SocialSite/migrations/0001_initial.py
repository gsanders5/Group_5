# Generated by Django 4.1.1 on 2022-09-21 22:23

import SocialSite.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FriendList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('userId', models.IntegerField()),
                ('numOfLikes', models.IntegerField(default='0')),
                ('content', models.TextField()),
                ('createdAt', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='PostList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('posts', models.ManyToManyField(blank=True, related_name='posts', to='SocialSite.post')),
            ],
        ),
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('bio', models.TextField()),
                ('email', models.EmailField(max_length=60, unique=True, verbose_name='email')),
                ('username', models.CharField(max_length=255, unique=True)),
                ('date_joined', models.DateTimeField(auto_now_add=True, verbose_name='date joined')),
                ('last_login', models.DateTimeField(auto_now=True, verbose_name='last login')),
                ('is_admin', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('profile_image', models.ImageField(blank=True, default=SocialSite.models.get_default_profile_image, max_length=255, null=True, upload_to=SocialSite.models.get_profile_image_filepath)),
                ('hide_email', models.BooleanField(default=True)),
                ('isPrivate', models.BooleanField(default='True')),
                ('friendsList', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='SocialSite.friendlist')),
                ('postList', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='SocialSite.postlist')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='postlist',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='poster', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='post',
            name='usersWhoLiked',
            field=models.ManyToManyField(blank=True, related_name='users_who_liked', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='friendlist',
            name='friends',
            field=models.ManyToManyField(blank=True, related_name='friends', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='friendlist',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL),
        ),
    ]
