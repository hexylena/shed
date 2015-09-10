from .models import Tag, Installable, Revision, SuiteRevision, GroupExtension
from rest_framework import serializers
from django.contrib.auth.models import User, Group


class GroupExtensionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupExtension


class GroupLessUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username')


class GroupSerializer(serializers.ModelSerializer):
    website = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    gpg_pubkey_id = serializers.SerializerMethodField()

    user_set = GroupLessUserSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = ('id', 'name', 'website', 'user_set', 'gpg_pubkey_id', 'description')
        read_only = ('id', 'name')

    def get_website(self, obj):
        return obj.groupextension.website

    def get_gpg_pubkey_id(self, obj):
        return obj.groupextension.gpg_pubkey_id

    def get_description(self, obj):
        return obj.groupextension.description


class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True, read_only=True)
    hashed_email = serializers.CharField(source='userextension.hashedEmail')
    display_name = serializers.CharField(source='userextension.display_name')

    class Meta:
        model = User
        fields = ('id', 'username', 'groups', 'hashed_email', 'display_name')


class RecursiveField(serializers.Serializer):
    # http://stackoverflow.com/a/22405982
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class TagListSerializer(serializers.ModelSerializer):
    number_of_repos = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = ('id', 'display_name', 'description', 'number_of_repos')

    def get_number_of_repos(self, obj):
        return obj.installable_set.count()


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


class TagDetailSerializer(serializers.ModelSerializer):
    installable_set = InstallableMetaSerializer(many=True, read_only=True)

    class Meta:
        model = Tag
        fields = ('id', 'display_name', 'description', 'installable_set')
        read_only = ('installable_set', )


class RevisionSerializer(serializers.ModelSerializer):
    dependencies = RecursiveField(many=True, read_only=True)
    installable = InstallableMetaSerializer(read_only=True)

    class Meta:
        model = Revision
        fields = ('id', 'version', 'commit_message', 'uploaded',
                  'installable', 'tar_gz_sha256', 'tar_gz_sig_available',
                  'replacement_revision', 'downloads', 'dependencies')


class InstallableSerializer(serializers.ModelSerializer):
    # List view
    tags = TagListSerializer(many=True, read_only=True)
    revision_set = serializers.StringRelatedField(
        many=True, read_only=True, required=False, allow_null=True)
    total_downloads = serializers.SerializerMethodField()
    last_updated = serializers.SerializerMethodField()

    homepage_url = serializers.CharField(required=False, allow_null=True)
    remote_repository_url = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = Installable
        fields = ('id', 'name', 'synopsis', 'description',
                  'remote_repository_url', 'homepage_url', 'repository_type',
                  'tags', 'revision_set', 'total_downloads', 'last_updated')

    def get_last_updated(self, obj):
        return obj.last_updated

    def get_total_downloads(self, obj):
        return obj.total_downloads


class InstallableWithRevisionSerializer(serializers.ModelSerializer):
    # Detail view
    tags = TagListSerializer(many=True, read_only=True)
    revision_set = RevisionSerializer(many=True, read_only=True,
                                      required=False, allow_null=True)
    can_edit = serializers.SerializerMethodField()
    total_downloads = serializers.SerializerMethodField()
    last_updated = serializers.SerializerMethodField()

    homepage_url = serializers.CharField(required=False, allow_null=True)
    remote_repository_url = serializers.CharField(required=False, allow_null=True)

    def get_can_edit(self, obj):
        return obj.can_edit(self.context['request'].user)

    def get_last_updated(self, obj):
        return obj.last_updated

    def get_total_downloads(self, obj):
        return obj.total_downloads

    class Meta:
        model = Installable
        fields = ('id', 'name', 'synopsis', 'description',
                  'remote_repository_url', 'homepage_url', 'repository_type',
                  'tags', 'can_edit', 'revision_set', 'last_updated', 'total_downloads')


class SuiteRevisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuiteRevision
        fields = ('id', 'version', 'commit_message', 'installable',
                  'contained_revisions')
