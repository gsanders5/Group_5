# Generated by Django 4.1.1 on 2022-09-18 06:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SocialSite', '0002_auto_20220918_0612'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='isAdmin',
            field=models.BooleanField(default='False'),
        ),
    ]
