import hashlib
from django.db import models
from django.contrib.auth.models import User, Group

INSTALLABLE_TYPES = (
    (0, 'package'),
    (1, 'tool'),
    (2, 'datatype'),
    (3, 'suite'),
    (4, 'viz'),
    (5, 'gie')
)


class UserExtension(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    display_name = models.CharField(max_length=64, blank=True)
    api_key = models.CharField(max_length=32, unique=True, blank=True)
    gpg_pubkey_id = models.CharField(max_length=16)
    github = models.IntegerField()

    @property
    def hashedEmail(self):
        return hashlib.md5(self.user.email).hexdigest()


class GroupExtension(models.Model):
    group = models.OneToOneField(Group, primary_key=True)

    description = models.TextField(blank=False)
    website = models.TextField()
    gpg_pubkey_id = models.CharField(max_length=16)


class Tag(models.Model):
    display_name = models.CharField(max_length=120, blank=False)
    description = models.TextField(blank=False)

    def __str__(self):
        return self.display_name


class Installable(models.Model):
    # TODO: prevent renaming
    name = models.CharField(max_length=120, blank=False)
    synopsis = models.TextField(blank=False)
    description = models.TextField(blank=False)

    remote_repository_url = models.TextField()
    homepage_url = models.TextField()

    repository_type = models.IntegerField(choices=INSTALLABLE_TYPES, blank=False)

    tags = models.ManyToManyField(Tag)

    user_access = models.ManyToManyField(User, blank=True)
    group_access = models.ManyToManyField(Group, blank=True)

    def can_edit(self, user):
        if user in self.user_access.all():
            return True

        for group in user.groups.all():
            if group in self.group_access.all():
                return True

        return False

    @property
    def total_downloads(self):
        return sum([
            rev.downloads for rev in self.revision_set.all()
        ])

    @property
    def last_updated(self):
        return self.revision_set.order_by('-uploaded').first().uploaded

    def __str__(self):
        return self.name


class Revision(models.Model):
    # This must be unique per installable.
    version = models.CharField(max_length=12, blank=False)
    commit_message = models.TextField(blank=False)
    public = models.BooleanField(default=True, blank=False)
    uploaded = models.DateTimeField(blank=False)
    # Link back to our parent installable
    installable = models.ForeignKey(Installable)
    # Archive sha256sum for transport integrity
    tar_gz_sha256 = models.CharField(max_length=64, blank=False)
    # No need to store in an API accessible manner, just on disk.
    # Maybe should have a toolshed GPG key and sign all packages with that.
    tar_gz_sig_available = models.BooleanField(default=False, blank=False)

    # If a user has this version of this package installed, what should they
    # upgrade to. Need to provide a (probably expensive) method to calculate a
    # full upgrade path?
    replacement_revision = models.ForeignKey('self', blank=True, null=True)

    # Track downloads
    downloads = models.IntegerField(default=0)

    # Dependency graph data
    dependencies = models.ManyToManyField(
        'self',
        through='RevisionDependency',
        blank=True,
        symmetrical=False,
        related_name='used_in'
    )

    def __str__(self):
        return '%s %s' % (self.installable.name, self.version)


class RevisionDependency(models.Model):
    from_revision = models.ForeignKey(Revision, related_name='from_revision')
    to_revision = models.ForeignKey(Revision, related_name='to_revision')


class SuiteRevision(models.Model):
    version = models.CharField(max_length=12, blank=False)
    commit_message = models.TextField(blank=False)
    installable = models.ForeignKey(Installable)
    contained_revisions = models.ManyToManyField(Revision)

    def __str__(self):
        return 'Suite %s %s' % (self.installable.name, self.version)
