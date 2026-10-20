from urllib.parse import urlsplit

from django.conf import settings
from django.middleware.csrf import CsrfViewMiddleware


class LocalDevelopmentCsrfViewMiddleware(CsrfViewMiddleware):
    """Trust localhost dev-server ports in DEBUG while keeping production strict."""

    def _origin_verified(self, request):
        origin = request.META.get("HTTP_ORIGIN", "")
        if settings.DEBUG and origin:
            try:
                parsed = urlsplit(origin)
                is_local_origin = (
                    parsed.scheme == ("https" if request.is_secure() else "http")
                    and parsed.hostname in {"localhost", "127.0.0.1"}
                    and not parsed.path
                    and not parsed.query
                    and not parsed.fragment
                )
            except ValueError:
                is_local_origin = False

            if is_local_origin:
                return True

        return super()._origin_verified(request)


class StaticHtmlRevalidationMiddleware:
    """Revalidate static app sources so tabs receive current code and styles."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        static_prefix = settings.STATIC_URL
        if (
            request.path.startswith(static_prefix)
            and request.path.lower().endswith((".html", ".js", ".css"))
            and response.status_code == 200
        ):
            response["Cache-Control"] = "no-cache, must-revalidate"
        return response
