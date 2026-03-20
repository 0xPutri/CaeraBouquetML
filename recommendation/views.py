from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import RecommendationService
from .apps import RecommendationConfig

class MLHealthCheckView(APIView):
    def get(self, request):
        is_ready = (
            RecommendationConfig.sim_matrix is not None and 
            RecommendationConfig.df_products is not None
        )

        if is_ready:
            return Response(
                {
                    "status": "success",
                    "message": "ML Service is healthy and models are loaded.",
                    "details": {
                        "sim_matrix_shape": RecommendationConfig.sim_matrix.shape,
                        "reference_products_count": len(RecommendationConfig.df_products)
                    }
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {
                "status": "error",
                "message": "ML Service is unavailable. Artifacts failed to load."
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )

class ProductRecommendationView(APIView):
    def get(self, request, product_id):
        top_n = int(request.query_params.get('top_n', 5))

        result = RecommendationService.get_by_product(product_id, top_n)

        if "error" in result:
            return Response(
                {"status": "error", "message": result["error"]}, 
                status=result["status"]
            )

        return Response(
            {"status": "success", "data": result["data"]}, 
            status=status.HTTP_200_OK
        )

class EventRecommendationView(APIView):
    def get(self, request, event_type):
        top_n = int(request.query_params.get('top_n', 5))

        result = RecommendationService.get_by_event(event_type, top_n)

        if "error" in result:
            return Response(
                {"status": "error", "message": result["error"]}, 
                status=result["status"]
            )
        
        return Response(
            {"status": "success", "data": result["data"]}, 
            status=status.HTTP_200_OK
        )