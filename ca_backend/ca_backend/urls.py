import sys
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from rest_framework import permissions


class SchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        RUNNING_DEVSERVER = (len(sys.argv) > 1 and sys.argv[1] == 'runserver')
        if not RUNNING_DEVSERVER:
            schema.schemes = ["https", "http"]
        else:
            schema.schemes = ["http", "https"]
        return schema

schema_view = get_schema_view(
    openapi.Info(
        title="CA_BACKEND API",
        default_version="v1",
        description="This is the Technex Site CA_BACKEND API.",
    ),
    public=True,
    generator_class=SchemaGenerator,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("auth/", include("Authentication.urls")),
    path("tasks/", include("Task.urls"))
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += [
        path(
            "",
            schema_view.with_ui("swagger", cache_timeout=0),
            name="schema-swagger-ui",
        )
    ]
