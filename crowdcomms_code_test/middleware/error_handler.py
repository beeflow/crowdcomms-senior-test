import json
import logging

from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponse
from rest_framework import status

from bunnies.models import TooManyBunniesInRabbitHole

request_logger = logging.getLogger("api.request.logger")

error_handler_middleware_responders = {
    ObjectDoesNotExist.__name__: "not_found_response",
    TooManyBunniesInRabbitHole.__name__: "too_many_bunnies",
    Http404.__name__: "not_found_response",
}


def get_http_response(exception_code, exception_message, http_status, details=None):
    error = get_error(exception_code, exception_message, details)

    return HttpResponse(json.dumps(error), status=http_status, content_type="application/json")


def get_error(exception_code, exception_message, details=None):
    error = {"error": {"code": exception_code, "message": exception_message}}
    if details:
        error["error"].update({"payload": details})

    return error


class ErrorHandlerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, _, exception):
        try:
            return getattr(self, error_handler_middleware_responders[exception.__class__.__name__])(exception)
        except KeyError:
            pass

    # noinspection PyMethodMayBeStatic
    def permission_denied_response(self, exception):
        return get_http_response(exception.status_code, str(exception), status.HTTP_403_FORBIDDEN)

    # noinspection PyMethodMayBeStatic
    def too_many_bunnies(self, exception):
        return get_http_response("", str(exception), status.HTTP_400_BAD_REQUEST)

    # noinspection PyMethodMayBeStatic
    def not_found_response(self, exception):
        return get_http_response(exception.status_code, str(exception), status.HTTP_404_NOT_FOUND)
