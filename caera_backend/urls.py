from django.urls import include, path
from recommendation.views import MLHealthCheckView

urlpatterns = [
    path('health/', MLHealthCheckView.as_view(), name='ml_health_check'),
    path('api/recommendations/', include('recommendation.urls')),
]