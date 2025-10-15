
import re
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from .models import PageVisit

EXCLUDED_PATHS = [
    r'^/static/',
    r'^/media/',
    r'^/admin/',
    r'^/api/',
    r'^/notifications/',
    r'^/__debug__/',
]

class PageVisitMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        if isinstance(request.user, AnonymousUser):
            return

        if request.method != 'GET':
            return

        path = request.path
        if any(re.match(pattern, path) for pattern in EXCLUDED_PATHS):
            return

        title = getattr(request, '_page_title', 'Untitled')

        visit, created = PageVisit.objects.get_or_create(
            user=request.user,
            url=path,
            defaults={'title': title}
        )
        if not created:
            visit.counter += 1
            visit.save(update_fields=['counter', 'visited'])