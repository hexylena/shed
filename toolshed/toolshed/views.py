from urlparse import parse_qsl
import json
import requests
# from rest_framework import status
# from rest_framework.permissions import AllowAny, IsAuthenticated
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from rest_framework_jwt.settings import api_settings
# from rest_framework_jwt.serializers import JSONWebTokenSerializer
from django.http import JsonResponse
from rest_framework_jwt.utils import jwt_payload_handler, jwt_encode_handler
from django.conf import settings
from django.contrib.auth.models import User
from api.models import UserExtension
from django.views.decorators.csrf import csrf_exempt

proxies = {
    "http": "http://localhost:8080",
    "https": "http://localhost:8080",
}


def generate_token(user):
    payload = jwt_payload_handler(user)

    return {
        'token': jwt_encode_handler(payload),
    }


@csrf_exempt
def github(request):
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
        r = requests.get(access_token_url, params=params, proxies=proxies, verify=False)
        access_token = dict(parse_qsl(r.text))
        headers = {'User-Agent': 'Satellizer'}

        # Step 2. Retrieve information about the current user.
        r = requests.get(users_api_url, params=access_token, headers=headers, proxies=proxies, verify=False)
        profile = json.loads(r.text)

        # Step 3. Create a new account or return an existing one.
        user = User.objects.filter(userextension__github=profile['id']).first()
        print User.objects.all()
        print User.objects.filter(userextension__github=profile['id']).all()
        print user
        if user:
            user.email = profile['email']
            user.save()
        else:
            user = User.objects.create_user(username=profile['login'],
                                            email=profile['email'],
                                            password=None)
            ue = UserExtension(
                github=profile['id'],
            )
            ue.save()
            user.userextension = ue
            user.save()

        return JsonResponse(generate_token(user))
    else:
        return JsonResponse({})
