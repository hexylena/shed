# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_userextension_display_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='revision',
            name='public',
        ),
    ]
