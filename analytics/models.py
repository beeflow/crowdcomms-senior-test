from django.conf import settings
from django.db import models


class UserVisit(models.Model):
    '''
    We'll track each time a user visited the site
    '''

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    last_seen = models.DateTimeField(auto_now=True)
    visits = models.PositiveIntegerField(default=0)
