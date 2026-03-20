from django.urls import path
from .views import ProductRecommendationView, EventRecommendationView, MLHealthCheckView

urlpatterns = [
    path('health/', MLHealthCheckView.as_view(), name='ml_health_check'),

    path('product/<str:product_id>/', ProductRecommendationView.as_view(), name='recom_product'),
    path('event/<str:event_type>/', EventRecommendationView.as_view(), name='recom_event'),
]