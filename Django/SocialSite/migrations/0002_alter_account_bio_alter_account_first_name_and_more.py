# Generated by Django 4.1.1 on 2022-10-02 22:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SocialSite', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='bio',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='account',
            name='first_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='account',
            name='last_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
