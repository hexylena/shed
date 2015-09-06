from toolshed import db
# Schema
INSTALLABLE_TYPES = ('repository_dependency', 'tool', 'suite', 'viz',
                     'interactive_environment')
tags = db.Table(
    'tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
    db.Column('installable_id', db.Integer, db.ForeignKey('installable.id')),
)
revisions = db.Table(
    'revisions',
    db.Column('installable_id', db.Integer, db.ForeignKey('installable.id')),
    db.Column('revision_id', db.Integer, db.ForeignKey('revision.id')),
)
suite_rr = db.Table(
    'suiterevision_revision',
    db.Column('suiterevision_id', db.Integer, db.ForeignKey('suite_revision.id')),
    db.Column('revision_id', db.Integer, db.ForeignKey('revision.id')),
)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.String(120), nullable=False)
    api_key = db.Column(db.String(32), unique=True)

    email = db.Column(db.String(120), unique=True, nullable=False)
    gpg_pubkey_id = db.Column(db.String(16))

    def __repr__(self):
        return '<User %s: %s>' % (self.id, self.display_name)


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.String(120), nullable=False)

    description = db.Column(db.String(), nullable=False)
    website = db.Column(db.String())
    gpg_pubkey_id = db.Column(db.String(16))

    def __repr__(self):
        return '<Group %s: %s>' % (self.id, self.display_name)


class UserGroupRelationship(db.Model):
    __tablename__ = 'user_group_relationship'
    id = db.Column('id', db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    user = db.relationship(User, backref="groups")
    group = db.relationship(Group, backref="users")

    permissions = db.Column(db.Integer)

    def __repr__(self):
        return '<Grant %s to %s in %s>' % (self.permissions, self.user, self.group)


class Installable(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(), nullable=False)

    remote_repository_url = db.Column(db.String())
    homepage_url = db.Column(db.String())

    repository_type = db.Column(db.Enum(*INSTALLABLE_TYPES), nullable=False)

    tags = db.relationship(
        'Tag', secondary=tags,
        backref=db.backref('installable', lazy='dynamic')
    )
    revisions = db.relationship(
        'Revision', secondary=revisions,
        backref=db.backref('installable', lazy='dynamic')
    )

    def __repr__(self):
        return '<Installable %s:%s>' % (self.id, self.name)


class InstallableUserAccessPermissions(db.Model):
    __tablename__ = 'installable_user_permissions'
    id = db.Column('id', db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship(User, backref="installable_user")

    installable_id = db.Column(db.Integer, db.ForeignKey('installable.id'))
    installable = db.relationship(Installable, backref="installable_user_permissions")

    permissions = db.Column(db.Integer)


class InstallableGroupAccessPermissions(db.Model):
    __tablename__ = 'installable_group_permissions'
    id = db.Column('id', db.Integer, primary_key=True)

    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    group = db.relationship(Group, backref="installable_group")

    installable_id = db.Column(db.Integer, db.ForeignKey('installable.id'))
    installable = db.relationship(Installable, backref="installable_group_permissions")

    permissions = db.Column(db.Integer, nullable=False)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(), nullable=False)


class Revision(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String(12), nullable=False)
    commit_message = db.Column(db.String(), nullable=False)
    public = db.Column(db.Boolean, default=True, nullable=False)
    uploaded = db.Column(db.DateTime, nullable=False)

    tar_gz_sha256 = db.Column(db.String(64), nullable=False)
    # No need to store in an API accessible manner, just on disk.
    # Maybe should have a toolshed GPG key and sign all packages with that.
    tar_gz_sig_available = db.Column(db.Boolean, default=False, nullable=False)

    # If a user has this version of this package installed, what should they
    # upgrade to. Need to provide a (probably expensive) method to calculate a
    # full upgrade path?
    replacement_revision = db.Column(db.Integer, db.ForeignKey('revision.id'))


class SuiteRevision(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String(12), nullable=False)
    commit_message = db.Column(db.String(), nullable=False)
    installable = db.Column(db.Integer, db.ForeignKey('installable.id'))

    contained_revisions = db.relationship(
        'Revision', secondary=suite_rr,
        backref=db.backref('suiterevision', lazy='dynamic')
    )

