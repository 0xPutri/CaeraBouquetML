from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import RecommendationService

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