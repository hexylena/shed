# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_remove_userextension_github_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userextension',
            name='api_key',
            field=models.CharField(unique=True, max_length=32, blank=True),
        ),
    ]
