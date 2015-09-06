from toolshed import app, db, jwt
from toolshed.models import User, Group, Installable, Tag, Revision, SuiteRevision
from toolshed.rules import api_user_authenticator, api_user_postprocess, api_user_postprocess_many
from flask.ext.restless import APIManager


def restless_jwt(*args, **kwargs):
    app.logger.debug("Verifying JWT ticket")
    pass
    # verify_jwt()
    # return True


api_manager = APIManager(
    app,
    flask_sqlalchemy_db=db,
    preprocessors={
        'POST': [restless_jwt],
        'PATCH_MANY': [restless_jwt],
        'PATCH_SINGLE': [restless_jwt],
    }
)



@jwt.authentication_handler
def authenticate(username, password):
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
)

installable_api = api_manager.create_api_blueprint(
    Installable,
    methods=methods,
    preprocessors={
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

