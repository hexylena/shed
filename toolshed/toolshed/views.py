import json
import requests
from api.models import UserExtension
from django.conf import settings
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework_jwt.utils import jwt_payload_handler, jwt_encode_handler
from urlparse import parse_qsl
import logging
log = logging.getLogger(__name__)


def generate_token(user):
    """
    Generate a JWT for the user.

    The token generally contains the following:

        {
            "username": "erasche",
            "orig_iat": 1441902926,
            "user_id": 5,
            "email": "esr@tamu.edu",
            "exp": 1442507726
        }

    """
    payload = jwt_payload_handler(user)

    return {
        'token': jwt_encode_handler(payload),
    }


@csrf_exempt
def github(request):
    """
    Complete server-side leg of github OAuth2 flow.

    This is mostly copied from satellizer, with appropriate changes for our
    database. The GET route shouldn't really be required, not sure why
    satellizer is making that request, but it wreaks all sorts of havock if
    it's removed, so we return an empty response + 200OK. No harm in that.
    """
    if request.method == 'POST':
        access_token_url = 'https://github.com/login/oauth/access_token'
        users_api_url = 'https://api.github.com/user'

        post_data = json.loads(request.body)
        params = {
            'client_id': post_data['clientId'],
            'redirect_uri': post_data['redirectUri'],  # 'http://192.168.11.54:8000/complete/github/',
            'client_secret': settings.SOCIAL_AUTH_GITHUB_SECRET,
            'code': post_data['code']
        }

        # Step 1. Exchange authorization code for access token.
        r = requests.get(access_token_url, params=params)
        access_token = dict(parse_qsl(r.text))
        headers = {'User-Agent': 'Satellizer'}

        # Step 2. Retrieve information about the current user.
        r = requests.get(users_api_url, params=access_token, headers=headers)
        profile = json.loads(r.text)

        # Step 3. Create a new account or return an existing one.
        user = User.objects.filter(userextension__github=profile['id']).first()
        if user:
            user.email = profile['email']
            user.userextension.display_name = profile['name']
            user.save()
        else:
            user = User.objects.create_user(username=profile['login'],
                                            email=profile['email'],
                                            password=None)
            ue = UserExtension(
                github=profile['id'],
                display_name=profile['name'],
            )
            ue.save()
            user.userextension = ue
            user.save()

        return JsonResponse(generate_token(user))
    else:
        return JsonResponse({})
