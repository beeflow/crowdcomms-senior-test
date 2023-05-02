from datetime import timedelta

from django.db.models import Sum
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from analytics.models import UserVisit


class HelloWorld(APIView):
    """
    Basic 'Hello World' view. Show our current API version, the current time, the number of recent visitors
    in the last 1 hour, and the total number of visitors and page visits
    """

    def get(self, request, format=None):
        this_hour = timezone.now().replace(minute=0, second=0, microsecond=0)
        one_hour_before = this_hour - timedelta(hours=1)

        user_visits = UserVisit.objects.all()

        data = {
            'version': 1.0,
            'time': timezone.now(),
            'recent_visitors': user_visits.filter(last_seen__range=(one_hour_before, this_hour)).count(),
            'all_visitors': user_visits.count(),
            'all_visits': user_visits.aggregate(Sum("visits"))["visits__sum"],
        }
        return Response(data)
