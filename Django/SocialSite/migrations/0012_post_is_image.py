# Generated by Django 4.1.1 on 2022-10-23 19:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SocialSite', '0011_rename_description_post_textcontent'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='is_image',
            field=models.BooleanField(default=False),
        ),
    ]
