from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bunnies.models import RabbitHole
from foxes.permissions import IsAFox
from foxes.serializers import NearbyRabbitHoleSerializer


# Create your views here.

@api_view(["GET"])
@permission_classes([IsAuthenticated & IsAFox])
def get_nearby_active_rabbit_holes(request):
    """
    As a fox, I want to be able to sniff out nearby populated rabbit holes
    Given my current latitude / longitude, return the location name + position + distance of the closest rabbit hole
    that contains at least one rabbit for my dinner, as a lat / lng pair
    """
    try:
        ser = NearbyRabbitHoleSerializer().to_representation(
          instance=RabbitHole.objects.get(owner=request.user)
        )

        return Response(data=ser.data)
    except ObjectDoesNotExist:
        raise Http404
