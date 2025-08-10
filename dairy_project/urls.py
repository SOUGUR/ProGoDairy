from django.urls import path, include
from django.contrib import admin
from strawberry.django.views import GraphQLView
from .schema import schema
from .views import homepage_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("graphql/", GraphQLView.as_view(schema=schema)),
    path("", include("suppliers.urls")),
    path("distribution/", include("distribution.urls")),
    path("bmcu/", include("collection_center.urls")),
    path("accounts/", include("accounts.urls")),
]

project_urls = [path("", homepage_view, name="home"),]


urlpatterns += project_urls