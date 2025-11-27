
from .models import PageVisit

def recent_pages(request):
    if not request.user.is_authenticated:
        return {'recent_pages': []}
    pages = PageVisit.objects.filter(user=request.user) \
        .order_by('-visited')[:5] \
        .values('url', 'title')
    return {'recent_pages': list(pages)}