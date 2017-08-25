# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-23 15:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('module', '0006_auto_20170822_0843'),
    ]

    operations = [
        migrations.RenameField(
            model_name='activity',
            old_name='tag',
            new_name='tags',
        ),
        migrations.AddField(
            model_name='collection',
            name='threshold',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='activity',
            name='difficulty',
            field=models.CharField(choices=[(b'low', 'low'), (b'medium', 'medium'), (b'high', 'high')], default=b'medium', max_length=32),
        ),
    ]