from django.contrib import admin
from .models import UserExtension, GroupExtension, Tag, Installable, Revision, SuiteRevision


@admin.register(UserExtension)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(GroupExtension)
class GroupAdmin(admin.ModelAdmin):
    pass


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(Installable)
class InstallableAdmin(admin.ModelAdmin):
    pass


@admin.register(Revision)
class RevisionAdmin(admin.ModelAdmin):
    pass


@admin.register(SuiteRevision)
class SuiteRevisionAdmin(admin.ModelAdmin):
    pass
