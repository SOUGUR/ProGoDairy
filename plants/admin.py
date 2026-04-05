from django.contrib import admin

from .models import Employee, Plant, Role, Silo

admin.site.register(Role)
admin.site.register(Employee)
admin.site.register(Plant)
admin.site.register(Silo)

