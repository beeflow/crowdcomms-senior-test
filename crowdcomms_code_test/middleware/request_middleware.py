import threading

from analytics.models import UserVisit


class RequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            user_visit = UserVisit.objects.get_or_create(user=request.user)[0]
            user_visit.visits += 1
            user_visit.save()

        return self.get_response(request)
