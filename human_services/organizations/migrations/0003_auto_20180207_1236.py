# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-02-07 12:36
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0002_auto_20171214_1957'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='organization',
            options={'ordering': ['id']},
        ),
    ]
