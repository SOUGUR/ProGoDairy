from django.contrib import admin
from .models import Tester, Batch,BatchMembership

admin.site.register(Tester)
admin.site.register(Batch)
admin.site.register(BatchMembership)
