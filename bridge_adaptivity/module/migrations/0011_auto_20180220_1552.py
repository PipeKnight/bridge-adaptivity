# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-02-20 15:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('module', '0010_auto_20180216_1150'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collectiongroup',
            name='course',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='course_groups', to='module.Course'),
        ),
        migrations.AlterField(
            model_name='course',
            name='slug',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
