from .models import Tag, Installable, Revision, SuiteRevision, GroupExtension
from rest_framework import serializers
from django.contrib.auth.models import User, Group


class GroupLessUserSerializer(serializers.ModelSerializer):
    """Serialize user without expanding the group list

    Partially to help with the fact that Group and User both serialize each
    other.
    """
    display_name = serializers.CharField(source='userextension.display_name', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'display_name', 'username')


class GroupSerializer(serializers.ModelSerializer):
    # http://stackoverflow.com/a/28733782
    website = serializers.URLField(source='groupextension.website', allow_blank=True, allow_null=True)
    description = serializers.CharField(source='groupextension.description', allow_blank=True, allow_null=True)
    gpg_pubkey_id = serializers.CharField(source='groupextension.gpg_pubkey_id', allow_blank=True, allow_null=True)

    # user_set_deref = GroupLessUserSerializer(many=True, read_only=True)
    can_edit = serializers.SerializerMethodField(read_only=True)
    user_set = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), default=GroupLessUserSerializer)

    class Meta:
        model = Group
        fields = ('id', 'name', 'website', 'user_set', 'gpg_pubkey_id',
                  'description', 'can_edit')#, 'user_set_deref')

    def update(self, instance, validated_data):
        import pprint; pprint.pprint(instance)
        import pprint; pprint.pprint(validated_data)
        return None

    def get_can_edit(self, obj):
        return obj in self.context['request'].user.groups.all()

    def create(self, validated_data):
        # Create the base group
        group = Group.objects.create(name=validated_data['name'])
        group.save()
        # Get our members list
        members = validated_data.get('members', [])
        user = self.context['request'].user
        # If the user forgot themselves, add them
        if user not in members:
            members.append(user)
        # And update our group
        group.user_set = members
        # Create the GE
        group_extension = GroupExtension(
            description=validated_data['groupextension']['description'],
            website=validated_data['groupextension']['website'],
            gpg_pubkey_id=validated_data['groupextension']['gpg_pubkey_id'],
        )
        group_extension.save()
        group.groupextension = group_extension
        group.save()
        return group


class UserSerializer(serializers.ModelSerializer):
    """Serialize Users (with their associated groups)
    """
    groups = GroupSerializer(many=True, read_only=True)
    hashed_email = serializers.CharField(source='userextension.hashedEmail')
    display_name = serializers.CharField(source='userextension.display_name')

    class Meta:
        model = User
        fields = ('id', 'username', 'groups', 'hashed_email', 'display_name')


class RecursiveField(serializers.Serializer):
    """Allows recursively expanding an object which references itself via an
    adjacency table. This is especially appropriate for our "dependencies"
    mechanism built with revisions, and allows revisions to produce a
    beautifully nested tree of dependencies and their dependencies.
    """
    # http://stackoverflow.com/a/22405982
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class TagListSerializer(serializers.ModelSerializer):
    """Serialize a List of Tags, with a brief overview of how many repos use
    the tag. The detail view expands the list of repos.
    """
    number_of_repos = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = ('id', 'display_name', 'description', 'number_of_repos')

    def get_number_of_repos(self, obj):
        return obj.installable_set.count()


class InstallableMetaSerializer(serializers.ModelSerializer):
    """Serialize metadata about an installable. When we view certain things
    like tag lists, we don't necessarily need the entire installable object
    including revisinos and their recursive dependencies. This just pulls out
    the things needed for rendering a link to the actual installable.
    """
    class Meta:
        model = Installable
        fields = ('id', 'name', 'synopsis',)


class TagDetailSerializer(serializers.ModelSerializer):
    """Tag detail, and pull metadata for all of the repos using this tag so we
    can link to them.
    """
    installable_set = InstallableMetaSerializer(many=True, read_only=True)

    class Meta:
        model = Tag
        fields = ('id', 'display_name', 'description', 'installable_set')
        read_only = ('installable_set', )


class RevisionSerializer(serializers.ModelSerializer):
    """Serialize everything needed for revision display, including a recursive
    tree of dependencies.
    """
    dependencies = RecursiveField(many=True, read_only=True)
    installable = InstallableMetaSerializer(read_only=True)

    class Meta:
        model = Revision
        fields = ('id', 'version', 'commit_message', 'uploaded',
                  'installable', 'tar_gz_sha256', 'tar_gz_sig_available',
                  'replacement_revision', 'downloads', 'dependencies')


class InstallableSerializer(serializers.ModelSerializer):
    """Serialize an installable for list view. (I.e. non-recursive revision dependencies)
    """
    # List view
    tags = TagListSerializer(many=True, read_only=True)
    revision_set = serializers.StringRelatedField(
        many=True, read_only=True, required=False, allow_null=True)
    total_downloads = serializers.SerializerMethodField()
    last_updated = serializers.SerializerMethodField()

    homepage_url = serializers.CharField(required=False, allow_blank=True)
    remote_repository_url = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Installable
        fields = ('id', 'name', 'synopsis', 'description',
                  'remote_repository_url', 'homepage_url', 'repository_type',
                  'tags', 'revision_set', 'total_downloads', 'last_updated')

    def get_last_updated(self, obj):
        return obj.last_updated

    def get_total_downloads(self, obj):
        return obj.total_downloads

    def create(self, validated_data):
        # Normally you just return this object, but we need to do more.
        i = Installable.objects.create(**validated_data)
        # Ensure the user creating the installable is added to list of who can
        # admin
        i.user_access = [
            self.context['request'].user
        ]
        i.save()
        return i


class InstallableWithRevisionSerializer(serializers.ModelSerializer):
    """Serialize an installable for detail view with full revision + dependency
    list.
    """
    tags = TagListSerializer(many=True, read_only=True)
    revision_set = RevisionSerializer(many=True, read_only=True)
    can_edit = serializers.SerializerMethodField()
    total_downloads = serializers.SerializerMethodField()
    last_updated = serializers.SerializerMethodField()

    homepage_url = serializers.CharField(required=False, allow_blank=True)
    remote_repository_url = serializers.CharField(required=False, allow_blank=True)

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
    """TODO:
    """
    class Meta:
        model = SuiteRevision
        fields = ('id', 'version', 'commit_message', 'installable',
                  'contained_revisions')
