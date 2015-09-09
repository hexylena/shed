from .models import Tag, Installable, Revision, SuiteRevision
from rest_framework import serializers


class TagSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'display_name', 'description')


class InstallableSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Installable
        fields = ('id', 'name', 'synopsis', 'description',
                  'remote_repository_url', 'homepage_url', 'repository_type',
                  'tags')


class RevisionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Revision
        fields = ('id', 'version', 'commit_message', 'public', 'uploaded',
                  'installable', 'tar_gz_sha256', 'tar_gz_sig_available',
                  'replacement_revision', 'downloads', 'dependencies')


class SuiteRevisionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SuiteRevision
        fields = ('id', 'version', 'commit_message', 'installable',
                  'contained_revisions')
