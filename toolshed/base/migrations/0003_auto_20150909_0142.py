# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_auto_20150909_0139'),
    ]

    operations = [
        migrations.AlterField(
            model_name='revision',
            name='dependencies',
            field=models.ManyToManyField(related_name='dependencies_rel_+', to='base.Revision', blank=True),
        ),
    ]
