import hashlib
from django.db import models
from django.contrib.auth.models import User, Group

INSTALLABLE_TYPES = (
    (0, 'tool'),
    (1, 'datatype'),
    (2, 'suite'),
    (3, 'viz'),
    (4, 'gie')
    # Wow I miss golang's iota. Just look at that! https://github.com/golang/go/wiki/Iota
)

PACKAGE_TYPES = (
    (0, 'conda'),
)


class UserExtension(models.Model):
    """Extension to the built-in user model, with a 1:1 mapping to users.
    """
    user = models.OneToOneField(User, primary_key=True)
    display_name = models.CharField(max_length=64, blank=True)
    api_key = models.CharField(max_length=32, unique=True, blank=True)
    gpg_pubkey_id = models.CharField(max_length=16)
    github = models.IntegerField()

    @property
    def hashedEmail(self):
        """Return an md5sum digest of the email address, appropriate for
        gravatars

        TODO: convert to a model field, we can denormalize a bit for not
        calculating a gazillion md5sums
        """
        return hashlib.md5(self.user.email).hexdigest()

    @property
    def gravatar_url(self):
        return '//www.gravatar.com/avatar/' + self.hashedEmail

    def __str__(self):
        return '%s <%s>' % (self.display_name, self.user.email)


class GroupExtension(models.Model):
    """Extension to the built-in group model, with a 1:1 mapping to groups.
    """
    group = models.OneToOneField(Group, primary_key=True)

    description = models.TextField(blank=False)
    website = models.TextField()
    gpg_pubkey_id = models.CharField(max_length=16)

    def __str__(self):
        return self.group.name


class Tag(models.Model):
    """User managed tags replace admin managed categories
    """
    display_name = models.CharField(max_length=120, blank=False)
    description = models.TextField(blank=False)

    def __str__(self):
        return self.display_name


class Installable(models.Model):
    """A single installable thing, equivalent to a repository in the old TS.

    Installables represent the repository level "thing", while Versions
    represent the real concrete installable version of a "thing".

    Installables have the usual metadata associated with TS repos, a set of
    tags, and then a set of users and groups with permissions to edit this
    repository. Being granted access to a repository grants the ability to change
    repository metadata, and to create new versions (releases).
    """
    # TODO: prevent renaming
    name = models.CharField(max_length=120, blank=False)
    synopsis = models.TextField(blank=False)
    description = models.TextField(blank=False)

    remote_repository_url = models.URLField()
    homepage_url = models.URLField()

    repository_type = models.IntegerField(choices=INSTALLABLE_TYPES, blank=False)

    tags = models.ManyToManyField(Tag)

    owner = models.ForeignKey(User, related_name='creator')
    user_access = models.ManyToManyField(User, blank=True)
    group_access = models.ManyToManyField(Group, blank=True)

    def can_edit(self, user):
        """Is the user allowed to edit the repo.

        This method will check a direct user access level, as well as via groups.
        """
        if user == self.owner:
            return True

        if user in self.user_access.all():
            return True

        for group in user.groups.all():
            if group in self.group_access.all():
                return True

        return False

    @property
    def total_downloads(self):
        """Query to find the sum of downloads for each version
        """
        return sum([
            rev.downloads for rev in self.version_set.all()
        ])

    @property
    def last_updated(self):
        """Return the upload date of the most recent version
        """
        v = self.latest_version
        if v is None:
            return None
        else:
            return v.uploaded

    @property
    def latest_version(self):
        """Return the upload date of the most recent version
        """
        if self.version_set.all().exists():
            return self.version_set.order_by('-uploaded').first()
        else:
            return None

    def __str__(self):
        return self.name


class PackageDependency(models.Model):
    """PackageDependencies are external dependencies not tracked by the TS.
    """
    type = models.IntegerField(choices=PACKAGE_TYPES, blank=False)
    identifier = models.CharField(max_length=32)
    package_version = models.CharField(max_length=16)

    class Meta:
        verbose_name_plural='Package dependencies'

    def __str__(self):
        return '{0.identifier}=={0.package_version}'.format(self)


class Version(models.Model):
    """A single version/version/release of a repository.

    In the old system, changeset IDs were the unique component of a version.
    We're replacing that with the actual version encoded in the file, and the
    hard requirement that they absolutely must be unique within an installable.
    This means we can get rid of two ugly identifiers (``version.id``,
    ``version.changeset_id``) and replace with a single human-readable
    ``version.version``.

    Versions must have an sha256sum, generated on the server side,
    hopefully checked against the uploading client. This is to provide
    transport integrity.

    Versions may have a GPG signature associated to them, signed with a user
    or group GPG key.

    Versions may specify a replacement version. I haven't fully figured out
    how I want that to work, but essentially it should point to the version
    you should upgrade to from the version you're currently looking at. Say
    Alice, Bob, and Charlie all have a different implementation of foobar 0.12,
    in the heydey of tool development. They recognise that this is a problem,
    and band together as the Galaxy foobar developers in a group. With the
    release of foobar 1.0, they've coordinated a great DatasetCollection
    enabled version of the foobar package and make a single release. At that
    time, they can adjust all of their individual repositories to say "point to
    foobar 1.0 from group bazqux." On the Galaxy admin side, it should simply
    say something like "Upgrade foobar 0.12 from Alice" and "The administrator
    foobar 0.12 from Alice's repository has specified that their version is
    replaced with foobar 1.0 from bazqux" giving the admin some assurance that
    this is intended.

    Versions may have dependencies. These are not really user-editable online,
    and must be parsed from tool_dependencies.xml files. This is stored as an
    asymmetrical adjacency table. Versions point to other versions.
    """
    # This must be unique per installable.
    version = models.CharField(max_length=12, blank=False)
    commit_message = models.TextField(blank=False)
    uploaded = models.DateTimeField(blank=False)
    # Link back to our parent installable
    installable = models.ForeignKey(Installable, blank=False)
    # Archive sha256sum for transport integrity
    tar_gz_sha256 = models.CharField(max_length=64)
    # No need to store in an API accessible manner, just on disk.
    # Maybe should have a toolshed GPG key and sign all packages with that.
    tar_gz_sig_available = models.BooleanField(default=False, blank=False)

    # If a user has this version of this package installed, what should they
    # upgrade to. Need to provide a (probably expensive) method to calculate a
    # full upgrade path?
    replacement_version = models.ForeignKey('self', blank=True, null=True, related_name='upgrade_to')

    # Track downloads
    downloads = models.IntegerField(default=0)

    # Dependency graph data
    dependencies = models.ManyToManyField(
        'self',
        through='VersionDependency',
        blank=True,
        symmetrical=False,
        related_name='used_in'
    )

    # Conda dependencies
    package_dependencies = models.ManyToManyField(PackageDependency)

    def __str__(self):
        return '%s %s' % (self.installable.name, self.version)


class VersionDependency(models.Model):
    """Linking table for versions.

    This may not be needed, but everything works? So we're not touching it.
    Maybe someone will have metadata they wish to add to dependencies later on.
    """
    from_version = models.ForeignKey(Version, related_name='from_version')
    to_version = models.ForeignKey(Version, related_name='to_version')

    def __str__(self):
        return 'dependency %s -> %s' % (self.from_version, self.to_version)


class SuiteVersion(models.Model):
    """SuiteVersions are a bit special: they're like an Version in that they
    have a parent installable, and that a SuiteVersion represents a single
    iteration of a suite. However, since they're metapackages and lack
    downloadables, they're unlike versions enough that we have to separate the
    model out.

    This feels like a very weak rationalization. Maybe suites should be
    completely removed and just merged with versions.
    """
    version = models.CharField(max_length=12, blank=False)
    commit_message = models.TextField(blank=False)
    installable = models.ForeignKey(Installable)
    contained_versions = models.ManyToManyField(Version)

    def __str__(self):
        return 'Suite %s %s' % (self.installable.name, self.version)
