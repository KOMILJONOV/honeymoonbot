# Generated by Django 4.0.6 on 2022-07-30 11:20

import bot.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_admin',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='post',
            name='media',
            field=models.FileField(blank=True, null=True, upload_to='media/', validators=[bot.models.file_size]),
        ),
    ]