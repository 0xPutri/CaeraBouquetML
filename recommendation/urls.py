from django.urls import path
from .views import ProductRecommendationView, EventRecommendationView

urlpatterns = [
    path('product/<str:product_id>/', ProductRecommendationView.as_view(), name='recom_product'),
    path('event/<str:event_type>/', EventRecommendationView.as_view(), name='recom_event'),
]