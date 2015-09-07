import time
import requests
from urlparse import parse_qsl
import json
from toolshed import app, db, jwt
from toolshed.models import User, Group, Installable, Tag, Revision, SuiteRevision
from toolshed.rules import api_user_authenticator, api_user_postprocess, api_user_postprocess_many, ensure_user_attached_to_group
from flask.ext.restless import APIManager
from flask import request, jsonify
from flask.ext.jwt import jwt_required, current_user, verify_jwt


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
    return {
        'user_id': user.id,
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
        'PATCH_SINGLE': [],
        'POST': [],
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
    methods=methods
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


@app.route('/')
def root():
    return app.send_static_file('index.html')
