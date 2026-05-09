from django.urls import include, path
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from recommendation.views import MLHealthCheckView

urlpatterns = [
    path('favicon.ico', RedirectView.as_view(url='/static/icons/favicon.ico', permanent=True)),
    path('health/', MLHealthCheckView.as_view(), name='ml_health_check'),
    path('api/recommendations/', include('recommendation.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)