# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('display_name', models.CharField(unique=True, max_length=120)),
                ('description', models.TextField()),
                ('website', models.TextField()),
                ('gpg_pubkey_id', models.CharField(max_length=16)),
            ],
        ),
        migrations.CreateModel(
            name='Installable',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=120)),
                ('synopsis', models.TextField()),
                ('description', models.TextField()),
                ('remote_repository_url', models.TextField()),
                ('homepage_url', models.TextField()),
                ('repository_type', models.IntegerField(choices=[(0, b'package'), (1, b'tool'), (2, b'datatype'), (3, b'suite'), (4, b'viz'), (5, b'gie')])),
                ('group_access', models.ManyToManyField(to='base.Group', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Revision',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('version', models.CharField(max_length=12)),
                ('commit_message', models.TextField()),
                ('public', models.BooleanField(default=True)),
                ('uploaded', models.DateTimeField()),
                ('tar_gz_sha256', models.CharField(max_length=64)),
                ('tar_gz_sig_available', models.BooleanField(default=False)),
                ('downloads', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='RevisionDependency',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('from_revision', models.ForeignKey(related_name='from_revision', to='base.Revision')),
                ('to_revision', models.ForeignKey(related_name='to_revision', to='base.Revision')),
            ],
        ),
        migrations.CreateModel(
            name='SuiteRevision',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('version', models.CharField(max_length=12)),
                ('commit_message', models.TextField()),
                ('contained_revisions', models.ManyToManyField(to='base.Revision')),
                ('installable', models.ForeignKey(to='base.Installable')),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('display_name', models.CharField(max_length=120)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('display_name', models.CharField(max_length=120)),
                ('api_key', models.CharField(unique=True, max_length=32)),
                ('email', models.CharField(unique=True, max_length=120)),
                ('gpg_pubkey_id', models.CharField(max_length=16)),
                ('github', models.CharField(unique=True, max_length=32)),
                ('github_username', models.CharField(max_length=64)),
                ('github_repos_url', models.CharField(max_length=128)),
            ],
        ),
        migrations.AddField(
            model_name='revision',
            name='dependencies',
            field=models.ManyToManyField(related_name='used_in', through='base.RevisionDependency', to='base.Revision', blank=True),
        ),
        migrations.AddField(
            model_name='revision',
            name='installable',
            field=models.ForeignKey(to='base.Installable'),
        ),
        migrations.AddField(
            model_name='revision',
            name='replacement_revision',
            field=models.ForeignKey(blank=True, to='base.Revision', null=True),
        ),
        migrations.AddField(
            model_name='installable',
            name='tags',
            field=models.ManyToManyField(to='base.Tag'),
        ),
        migrations.AddField(
            model_name='installable',
            name='user_access',
            field=models.ManyToManyField(to='base.User', blank=True),
        ),
        migrations.AddField(
            model_name='group',
            name='members',
            field=models.ManyToManyField(to='base.User'),
        ),
    ]
