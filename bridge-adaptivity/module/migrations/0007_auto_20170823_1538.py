# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-23 15:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('module', '0006_auto_20170822_0843'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='source_launch_url',
            field=models.URLField(max_length=255, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='activity',
            unique_together=set([('source_launch_url', 'collection')]),
        ),
    ]