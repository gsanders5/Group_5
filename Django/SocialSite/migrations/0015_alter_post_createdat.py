# Generated by Django 4.1.1 on 2022-10-24 00:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SocialSite', '0014_alter_post_textcontent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='createdAt',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
