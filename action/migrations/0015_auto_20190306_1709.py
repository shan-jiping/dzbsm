# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2019-03-06 09:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('action', '0014_short_task_command'),
    ]

    operations = [
        migrations.AlterField(
            model_name='short_task',
            name='command',
            field=models.CharField(blank=True, max_length=1000, null=True, verbose_name='\u8fd0\u884c\u547d\u4ee4'),
        ),
        migrations.AlterField(
            model_name='short_task',
            name='end_time',
            field=models.DateTimeField(null=True, verbose_name='\u7ed3\u675f\u65f6\u95f4'),
        ),
    ]
