# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='revision',
            name='dependencies',
            field=models.ManyToManyField(related_name='dependencies_rel_+', null=True, to='base.Revision', blank=True),
        ),
        migrations.AlterField(
            model_name='revision',
            name='replacement_revision',
            field=models.ForeignKey(blank=True, to='base.Revision', null=True),
        ),
    ]
