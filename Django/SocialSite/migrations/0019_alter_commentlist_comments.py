# Generated by Django 4.1.1 on 2022-10-24 23:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('SocialSite', '0018_post_is_shared_post_post_shared_post_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commentlist',
            name='comments',
            field=models.OneToOneField(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='SocialSite.comment'),
        ),
    ]
