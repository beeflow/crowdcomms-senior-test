from rest_framework import exceptions
from rest_framework.authentication import SessionAuthentication as BaseSessionAuthentication


class SessionAuthentication(BaseSessionAuthentication):
    def authenticate(self, request):
        user = getattr(request._request, 'user', None)

        if not user or not user.is_active or not user.is_authenticated:
            raise exceptions.AuthenticationFailed("Unauthorised.")

        self.enforce_csrf(request)

        return user, None
