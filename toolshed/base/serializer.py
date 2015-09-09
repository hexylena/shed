from .models import Tag, Installable, Revision, SuiteRevision, UserExtension, GroupExtension
from rest_framework import serializers
from django.contrib.auth.models import User, Group
from social.apps.django_app.default.models import UserSocialAuth


class SocialAuthSerializer(serializers.ModelSerializer):
    service_username = serializers.SerializerMethodField()

    class Meta:
        model = UserSocialAuth
        fields = ('uid', 'service_username', 'provider')

    def get_service_username(self, obj):
        return obj.extra_data['login']


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupExtension
        fields = ('group.name')


class UserSerializer(serializers.ModelSerializer):
    social_auth = SocialAuthSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'social_auth')
        read_only = ('id', )


class RecursiveField(serializers.Serializer):
    # http://stackoverflow.com/a/22405982
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'display_name', 'description')


class RevisionSerializerNonRec(serializers.ModelSerializer):
    class Meta:
        model = Revision
        fields = ('id', 'version', 'commit_message', 'public', 'uploaded',
                  'installable', 'tar_gz_sha256', 'tar_gz_sig_available',
                  'replacement_revision', 'downloads', 'dependencies')


class InstallableMetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Installable
        fields = ('id', 'name', 'synopsis',)


class RevisionSerializer(serializers.ModelSerializer):
    dependencies = RecursiveField(many=True, read_only=True)
    installable = InstallableMetaSerializer(read_only=True)

    class Meta:
        model = Revision
        fields = ('id', 'version', 'commit_message', 'public', 'uploaded',
                  'installable', 'tar_gz_sha256', 'tar_gz_sig_available',
                  'replacement_revision', 'downloads', 'dependencies')


class InstallableSerializer(serializers.ModelSerializer):
    # List view
    tags = TagSerializer(many=True, read_only=True)
    # revision_set = RevisionSerializer(many=True, read_only=True)
    repository_type = serializers.CharField(source='get_repository_type_display')

    class Meta:
        model = Installable
        fields = ('id', 'name', 'synopsis', 'description',
                  'remote_repository_url', 'homepage_url', 'repository_type',
                  'tags', 'revision_set')


class InstallableWithRevisionSerializer(serializers.ModelSerializer):
    # Detail view
    tags = TagSerializer(many=True, read_only=True)
    revision_set = RevisionSerializer(many=True, read_only=True)
    repository_type = serializers.CharField(source='get_repository_type_display')
    can_edit = serializers.SerializerMethodField()

# https://github.com/login/oauth/authorize?state=kHvv2pt6fDF9PHCUqx19xEugNKnCR6ik
# &redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fcomplete%2Fgithub%2F
# &response_type=code
# &client_id=9ba85b7e5e5684e3
# 9ba85b7e5e5684e3fcd8

# https://github.com/login/oauth/authorize?
# client_id=1f8b1187fb518660c773
# &redirect_uri=https%3A%2F%2Fdbdesigner.net%2Fauth%2Fgithub%2Fcallback
# &response_type=code
# &state=d2233ffb9f63c5ec481378b95925aa05d0a28b28a38e035b
    def get_can_edit(self, obj):
        return obj.can_edit(self.context['request'].user)

    class Meta:
        model = Installable
        fields = ('id', 'name', 'synopsis', 'description',
                  'remote_repository_url', 'homepage_url', 'repository_type',
                  'tags', 'can_edit', 'revision_set')

        read_only_fields = ('id', 'name', 'can_edit', 'revision_set', 'repository_type')


class SuiteRevisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuiteRevision
        fields = ('id', 'version', 'commit_message', 'installable',
                  'contained_revisions')
