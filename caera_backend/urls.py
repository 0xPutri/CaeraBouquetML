from django.contrib import admin
from django.urls import include, path
from recommendation.views import MLHealthCheckView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', MLHealthCheckView.as_view(), name='ml_health_check'),
    path('api/recommendations/', include('recommendation.urls')),
]