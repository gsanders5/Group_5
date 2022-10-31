# Generated by Django 4.1.1 on 2022-10-24 21:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('SocialSite', '0017_rename_createdat_post_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='is_shared_post',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='post',
            name='shared_post',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='SocialSite.post'),
        ),
        migrations.AddField(
            model_name='post',
            name='usersWhoLiked',
            field=models.ManyToManyField(blank=True, related_name='users_who_liked', to=settings.AUTH_USER_MODEL),
        ),
    ]
