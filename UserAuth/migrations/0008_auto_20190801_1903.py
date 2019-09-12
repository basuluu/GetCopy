# Generated by Django 2.2.3 on 2019-08-01 19:03

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UserAuth', '0007_remove_file_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='time',
            field=models.DateTimeField(blank=True, default=datetime.datetime.now, null=True),
        ),
        migrations.AddField(
            model_name='file',
            name='url',
            field=models.URLField(blank=True, null=True),
        ),
    ]