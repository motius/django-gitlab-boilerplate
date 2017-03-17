from django.conf.urls import include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings

from rest_framework.routers import DefaultRouter
from rest_framework_swagger.views import get_swagger_view

# API Routes
router = DefaultRouter()

# API Docs
schema_view = get_swagger_view(title='Django API')

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^api/docs/$', schema_view),
    url(r'^api/', include(router.urls, namespace='api')),
    url(r'^api/auth/', include('rest_auth.urls')),
    url(r'^api/auth/registration/', include('rest_auth.registration.urls')),
]

# Static routes
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
