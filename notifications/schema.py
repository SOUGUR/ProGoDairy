import strawberry
from strawberry import auto
import strawberry_django
from .models import Notification
from strawberry.types import Info

@strawberry_django.type(Notification)
class NotificationType:
    id: auto
    message: auto
    created_at: auto

    # computed field: check if THIS user has read it
    @strawberry.field
    def is_read(self, info: Info) -> bool:
        user = info.context.request.user
        if not user.is_authenticated:
            return False
        return self.is_read_by(user)


@strawberry.type
class Query:
    @strawberry.field
    def my_notifications(self, info: Info) -> list[NotificationType]:
        """All notifications (system-wide), annotated with read/unread per user"""
        user = info.context.request.user
        if not user.is_authenticated:
            return []
        return Notification.objects.all().order_by("-created_at")


@strawberry.type
class Mutation:
    @strawberry.mutation
    def mark_notification_read(self, info: Info, notification_id: int) -> bool:
        """Mark a single notification as read by the logged-in user"""
        user = info.context.request.user
        if not user.is_authenticated:
            return False
        try:
            _= Notification.objects.get(id=notification_id)
            return True
        except Notification.DoesNotExist:
            return False
