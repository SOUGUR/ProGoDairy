from django.urls import path, include
from django.contrib import admin
from strawberry.django.views import GraphQLView
from .schema import schema
from .views import homepage_view, milk_market_dashboard

urlpatterns = [
    path("admin/", admin.site.urls),
    path("graphql/", GraphQLView.as_view(schema=schema)),
    path("", include("suppliers.urls")),
    path("distribution/", include("distribution.urls")),
    path("bmcu/", include("collection_center.urls")),
    path("accounts/", include("accounts.urls")),
    path("milk/", include("milk.urls")),
    path("__reload__/", include("django_browser_reload.urls")),
]

project_urls = [path("", homepage_view, name="home"),
                path("milk_market_dashboard", milk_market_dashboard, name="milk_market_dashboard"),
                ]


urlpatterns += project_urls