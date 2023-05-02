from django.conf import settings
from django.db import models
from django.db.models import QuerySet


class TooManyBunniesInRabbitHole(ValueError):
    ...


class RabbitHole(models.Model):
    '''
    Rabbits live in rabbit holes
    '''
    location = models.CharField(max_length=64, unique=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bunnies_limit = models.PositiveIntegerField(default=5)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self) -> str:
        return self.location


class BunniesQuerySet(QuerySet):
    def create(self, **kwargs):
        bunnies_limit = kwargs["home"].bunnies_limit
        if bunnies_limit == kwargs["home"].bunnies.count():
            raise TooManyBunniesInRabbitHole(f"Too many bunnies. Maximum allowed is {bunnies_limit}")

        return super().create(**kwargs)


class Bunny(models.Model):
    '''

    '''
    name = models.CharField(max_length=64)
    home = models.ForeignKey(RabbitHole, on_delete=models.CASCADE, related_name='bunnies')

    objects = BunniesQuerySet().as_manager()

    def __str__(self) -> str:
        return f"{self.name} ({self.id})"
