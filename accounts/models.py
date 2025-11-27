
from django.db import models
from django.contrib.auth.models import User
class PageVisit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.CharField(max_length=500)
    title = models.CharField(max_length=120, blank=True)
    visited = models.DateTimeField(auto_now=True) 
    counter = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('user', 'url')
        indexes = [models.Index(fields=['user', '-visited'])]

    def __str__(self):
        return f"{self.user.username} → {self.url}"