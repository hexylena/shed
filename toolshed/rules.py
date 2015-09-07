from flask_jwt import verify_jwt, current_user
from toolshed import app
from toolshed.models import User
import flask.ext.restless


# API ENDPOINTS
def api_user_authenticator(*args, **kwargs):
    target_user = User.query.filter(User.id == kwargs['instance_id']).scalar()
    if target_user is None:
        return None

    # Verify our ticket
    verify_jwt()

    app.logger.debug("Verifying user (%s) access to model (%s)", current_user.id, target_user.id)
    # So that current_user is available
    if target_user != current_user:
        raise flask.ext.restless.ProcessingException(description='Not Authorized', code=401)

    return None


def api_user_postprocess(result=None, **kw):
    __sanitize_user(result)


def api_user_postprocess_many(result=None, **kw):
    for i in result['objects']:
        __sanitize_user(i)


def __sanitize_user(result):
    user_id = None
    try:
        # Verify our ticket
        verify_jwt()
        user_id = current_user.id
    except Exception:
        # Here is an interesting case where we accept failure. If the user
        # isn't logged in, sanitize all the things by setting user_id to None.
        # No result['id'] should ever match None, so we should be safe from
        # leaking email/api_keys
        pass

    # So current_user is available
    if result['id'] != user_id:
        # Strip out API key, email
        for key in ('email', 'api_key', 'github'):
            if key in result:
                del result[key]
    return result
