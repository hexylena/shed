from django.contrib import admin
from .models import UserExtension, GroupExtension, Tag, Installable, Revision, SuiteRevision, PackageDependency


@admin.register(UserExtension)
class UserAdmin(admin.ModelAdmin):
    list_display = ['user', 'display_name', 'gpg_pubkey_id', 'photo']

    def photo(self, obj) :
        return '<img src="%s" />' % (obj.gravatar_url)

    photo.allow_tags = True



@admin.register(GroupExtension)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['group', 'description']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'description']


@admin.register(Installable)
class InstallableAdmin(admin.ModelAdmin):
    list_display = ['name', 'synopsis', 'owner']


@admin.register(Revision)
class RevisionAdmin(admin.ModelAdmin):
    list_display = ['installable', 'version', 'uploaded', 'downloads']


@admin.register(SuiteRevision)
class SuiteRevisionAdmin(admin.ModelAdmin):
    pass


@admin.register(PackageDependency)
class PackageDependencyAdmin(admin.ModelAdmin):
    list_display = ['type', 'identifier', 'version']
