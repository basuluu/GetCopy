# Generated by Django 2.2.3 on 2019-08-01 18:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UserAuth', '0004_auto_20190801_1853'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='time',
            field=models.TimeField(auto_now=True),
        ),
    ]