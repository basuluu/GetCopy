# Generated by Django 2.2.3 on 2019-08-01 18:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('UserAuth', '0005_auto_20190801_1853'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='file',
            name='url',
        ),
    ]