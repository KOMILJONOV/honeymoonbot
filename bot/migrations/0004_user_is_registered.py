# Generated by Django 4.0.6 on 2022-07-30 13:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0003_alter_user_name_alter_user_number_alter_user_region'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_registered',
            field=models.BooleanField(default=False),
        ),
    ]
