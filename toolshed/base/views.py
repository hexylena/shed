from rest_framework import views, status
from rest_framework.response import Response
from social.apps.django_app.utils import psa


@psa()
def auth_by_token(request, backend):
    """Decorator that creates/authenticates a user with an access_token"""
    print request, backend
    token = request.data.get('access_token')
    user = request.user
    print token, user
    user = request.backend.do_auth(
        access_token=request.data.get('access_token')
    )
    print user

    if user:
        return user
    else:
        return None


class FacebookView(views.APIView):
    """View to authenticate users through Facebook."""

    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        auth_token = request.DATA.get('access_token', None)
        backend = request.DATA.get('backend', None)
        if auth_token and backend:
            try:
                # Try to authenticate the user using python-social-auth
                user = auth_by_token(request, backend)
            except Exception,e:
                return Response({
                        'status': 'Bad request',
                        'message': 'Could not authenticate with the provided token.'
                    }, status=status.HTTP_400_BAD_REQUEST)
            if user:
                if not user.is_active:
                    return Response({
                        'status': 'Unauthorized',
                        'message': 'The user account is disabled.'
                    }, status=status.HTTP_401_UNAUTHORIZED)

                # This is the part that differs from the normal python-social-auth implementation.
                # Return the JWT instead.

                # Get the JWT payload for the user.
                payload = jwt_payload_handler(user)

                # Include original issued at time for a brand new token,
                # to allow token refresh
                if api_settings.JWT_ALLOW_REFRESH:
                    payload['orig_iat'] = timegm(
                        datetime.utcnow().utctimetuple()
                    )

                # Create the response object with the JWT payload.
                response_data = {
                    'token': jwt_encode_handler(payload)
                }

                return Response(response_data)
        else:
            return Response({
                    'status': 'Bad request',
                    'message': 'Authentication could not be performed with received data.'
            }, status=status.HTTP_400_BAD_REQUEST)





class SocialAuthView(views.APIView):
    """
    View to authenticate social auth tokens with python-social-auth. It accepts
    a token and backend. It will validate the token with the backend. If
    successful it returns the local user associated with the social user. If
    there is no associated user it will associate the current logged in user or
    create a new user if not logged in. The user is then logged in and returned
    to the client.
    """
    social_serializer = SocialAuthSerializer
    user_serializer = None

    def post(self, request):
        serializer = self.social_serializer(data=request.DATA,
                                            files=request.FILES)

        if serializer.is_valid():
            backend = serializer.data['backend']
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        strategy = load_strategy(request=request, backend=backend)
        try:
            kwargs = dict({(k, i) for k, i in serializer.data.items()
                          if k != 'backend'})
            user = request.user
            kwargs['user'] = user.is_authenticated() and user or None
            user = strategy.backend.do_auth(**kwargs)
        except AuthAlreadyAssociated:
            data = {
                'error_code': 'social_already_accociated',
                'status': 'Auth associated with another user.',
            }
            return Response(data, status=status.HTTP_403_FORBIDDEN)

        if not user:
            data = {
                'error_code': 'social_no_user',
                'status': 'No associated user.',
            }
            return Response(data, status=status.HTTP_403_FORBIDDEN)

        if not user.is_active:
            data = {
                'error_code': 'social_inactive',
                'status': 'Associated user is inactive.',
            }
            return Response(data, status=status.HTTP_403_FORBIDDEN)

        _do_login(strategy, user)

        if not self.user_serializer:
            msg = 'SocialAuthView.user_serializer should be a serializer.'
            raise ImproperlyConfigured(msg)
        serializer = self.user_serializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


