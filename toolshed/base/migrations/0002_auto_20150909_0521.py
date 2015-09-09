# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userextension',
            name='display_name',
        ),
        migrations.RemoveField(
            model_name='userextension',
            name='email',
        ),
        migrations.RemoveField(
            model_name='userextension',
            name='github',
        ),
        migrations.RemoveField(
            model_name='userextension',
            name='github_repos_url',
        ),
        migrations.RemoveField(
            model_name='userextension',
            name='github_username',
        ),
    ]
