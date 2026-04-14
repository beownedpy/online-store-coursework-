import time
import logging

logger = logging.getLogger(__name__)

class RequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.monotonic()
        response = self.get_response(request)
        duration = round((time.monotonic() - start) * 1000, 2)
        logger.info(f"{request.method} {request.path} {response.status_code} {duration}ms")
        return response
