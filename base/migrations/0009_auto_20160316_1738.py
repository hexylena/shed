# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-03-16 17:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0008_version_changeset_revision'),
    ]

    operations = [
        migrations.AlterField(
            model_name='version',
            name='version',
            field=models.CharField(max_length=64),
        ),
    ]