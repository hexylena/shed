# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20150909_1903'),
    ]

    operations = [
        migrations.AddField(
            model_name='userextension',
            name='display_name',
            field=models.CharField(max_length=64, blank=True),
        ),
    ]
