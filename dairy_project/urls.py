
from django.urls import path, include
from django.contrib import admin
from strawberry.django.views import GraphQLView
from .schema import schema 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('graphql/', GraphQLView.as_view(schema=schema)), 
    path('', include('suppliers.urls')), 
    path('distribution/', include('distribution.urls')), 
    path('bmcu/', include('collection_center.urls')), 
]





