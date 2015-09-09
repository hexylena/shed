import os
import datetime
import shutil
import time
import requests
from urlparse import parse_qsl
import json
from toolshed import app, db, jwt, upload_path
from toolshed.models import User, Group, Installable, Tag, Revision, SuiteRevision
from toolshed.rules import api_user_authenticator, api_user_postprocess, \
    api_user_postprocess_many, ensure_user_attached_to_group, \
    ensure_user_attached_to_repo, ensure_user_access_to_repo
from flask.ext.restless import APIManager, ProcessingException
from flask import request, jsonify
from flask.ext.jwt import jwt_required, current_user, verify_jwt

from toolshed.galaxy import locate_version_number
import tempfile


def restless_jwt(*args, **kwargs):
    app.logger.debug("Verifying JWT ticket")
    pass


api_manager = APIManager(
    app,
    flask_sqlalchemy_db=db,
    preprocessors={
        'POST': [restless_jwt],
        'PATCH_MANY': [restless_jwt],
        'PATCH_SINGLE': [restless_jwt],
    }
)


@jwt.payload_handler
def make_payload(user):
    groups = [x[0] for x in
              db.session.query(Group.id)
              .join('members')
              .filter(User.id == user.id)
              .all()
              ]

    return {
        'user_id': user.id,
        'group_ids': groups,
        'username': user.display_name,
        'exp': time.time() + app.config['JWT_EXPIRATION_DELTA'],
    }


@jwt.authentication_handler
def authenticate(username):
    user = User.query.filter(User.email == username).scalar()
    if user is not None:
        return user


@jwt.user_handler
def load_user(payload):
    return User.query.filter(User.id == payload['user_id']).scalar()


@app.route('/auth/refresh', methods=['GET'])
def refresh_token():
    verify_jwt()
    payload = jwt.payload_callback(current_user)
    new_token = jwt.encode_callback(payload)
    return jwt.response_callback(new_token)


@app.route('/api/revision', methods=['POST'])
def create_revision():
    try:
        temp_upload = tempfile.NamedTemporaryFile(prefix='ts.upload.', delete=False)
        temp_upload.close()

        # Store the file to the temp path
        f = request.files['file']
        f.save(temp_upload.name)
    except Exception, e:
        app.logger.error(e)
        raise ProcessingException(description='Upload error', code=400)

    installable_sent_id = json.loads(request.form['installable'])['id']
    installable = Installable.query.filter(Installable.id == int(installable_sent_id)).one()

    # TODO san request.form

    # Examine the archive to pull out version number
    rev_kwargs = {
        'version': locate_version_number(temp_upload.name),
        'commit_message': request.form['commit'],
        'public': 1 if request.form['pub'] == 'true' else 0,
        'uploaded': datetime.datetime.utcnow(),
        'tar_gz_sha256': 'deadbeefcafe',  # TODO!!!
        'tar_gz_sig_available': True,
        'parent_installable': installable,
    }

    r = Revision(**rev_kwargs)  # noqa

    db.session.add(r)
    db.session.commit()

    output_name = '%s-%s.tar.gz' % (installable.name, rev_kwargs['version'])
    output_path = os.path.join(upload_path, output_name)
    shutil.move(temp_upload.name, output_path)

    output_sig = output_path + '.asc'
    with open(output_sig, 'w') as handle:
        handle.write(request.form['sig'])

    return jsonify({'revision_id': r.id})


methods = ['GET', 'POST', 'PATCH']
user_api = api_manager.create_api_blueprint(
    User,
    methods=methods,
    preprocessors={
        'PATCH_SINGLE': [api_user_authenticator],
        'POST': [api_user_authenticator]
    },
    # Sanitize confidential info
    postprocessors={
        'GET_SINGLE': [api_user_postprocess],
        'GET_MANY': [api_user_postprocess_many]
    }
)

group_api = api_manager.create_api_blueprint(
    Group,
    methods=methods,
    postprocessors={
        'POST': [ensure_user_attached_to_group],
    }
)

installable_api = api_manager.create_api_blueprint(
    Installable,
    methods=methods,
    # Updates need to verify access to repository.
    preprocessors={
        'PATCH_SINGLE': [ensure_user_access_to_repo],
    },
    postprocessors={
        'POST': [ensure_user_attached_to_repo],
    }
)

tag_api = api_manager.create_api_blueprint(
    Tag,
    methods=methods
)

revision_api = api_manager.create_api_blueprint(
    Revision,
    methods=methods
)

suite_revision_api = api_manager.create_api_blueprint(
    SuiteRevision,
    methods=['GET'],
    # PATCHing of releases is NOT permitted. POSTs are handled elsewhere
)

app.register_blueprint(user_api)
app.register_blueprint(group_api)
app.register_blueprint(installable_api)
app.register_blueprint(tag_api)
app.register_blueprint(revision_api)
app.register_blueprint(suite_revision_api)


@jwt_required()
def parse_token():
    print current_user
    return current_user


def generate_token(user):
    payload = jwt.payload_callback(user)
    token = jwt.encode_callback(payload)
    return token


@app.route('/auth/whoami', methods=['GET'])
def whoami():
    verify_jwt()
    return jsonify({
        'id': current_user.id,
        'display_name': current_user.display_name,
        'api_key': current_user.api_key,
    })


@app.route('/auth/github', methods=['POST'])
def github():
    access_token_url = 'https://github.com/login/oauth/access_token'
    users_api_url = 'https://api.github.com/user'

    params = {
        'client_id': request.json['clientId'],
        'redirect_uri': request.json['redirectUri'],
        'client_secret': app.config['GITHUB_SECRET'],
        'code': request.json['code']
    }

    # Step 1. Exchange authorization code for access token.
    r = requests.get(access_token_url, params=params)
    access_token = dict(parse_qsl(r.text))
    headers = {'User-Agent': 'Satellizer'}

    # Step 2. Retrieve information about the current user.
    r = requests.get(users_api_url, params=access_token, headers=headers)
    profile = json.loads(r.text)

    # Step 3. Create a new account or return an existing one.
    user = User.query.filter_by(github=profile['id']).first()
    if user:
        # Update the user if their data has changed
        user['display_name'] = profile['name']
        user['email'] = profile['email']
        user['github'] = profile['id']
        user['github_username'] = profile['login']
        user['github_repos_url'] = profile['repos_url']
        db.session.add(user)
        db.session.commit()

        return jsonify({'token': generate_token(user)})

    user = User(
        display_name=profile['name'],
        email=profile['email'],

        github=profile['id'],
        github_username=profile['login'],
        github_repos_url=profile['repos_url'],
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({'token': generate_token(user)})


@app.before_request
def track_package_requests(*args, **kwargs):
    """
    Track requests for the .tar.gz files
    """
    if request.path.startswith('/uploads/') and request.path.endswith('.tar.gz'):
        try:
            archive = request.path.split('/')[2]
            # TODO: validation on archive name + version variables
            # archive_name = [A-Za-z0-9_]
            # version = [0-9.-a-z]
            archive = archive.rstrip('.tar.gz')
            (archive_name, archive_version) = archive.split('-', 1)
            print archive_name, archive_version
            revision = Revision.query \
                .filter(Revision.version == archive_version) \
                .filter(Installable.name == archive_name).scalar()

            # Update number of downloads
            revision.downloads = Revision.c.downloads + 1
        except Exception:
            # It's not the end of the world if we don't catch an install
            pass


@app.route('/')
def root():
    return app.send_static_file('index.html')
