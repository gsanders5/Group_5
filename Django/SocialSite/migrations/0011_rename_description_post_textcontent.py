# Generated by Django 4.1.1 on 2022-10-23 18:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('SocialSite', '0010_alter_account_profile_image'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='description',
            new_name='textContent',
        ),
    ]