from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import logging
from .services import RecommendationService
from .apps import RecommendationConfig

logger = logging.getLogger(__name__)


def _resolve_top_n(request, default: int = 5, minimum: int = 1, maximum: int = 20):
    raw_top_n = request.query_params.get('top_n', default)
    try:
        value = int(raw_top_n)
    except (TypeError, ValueError):
        return None, "Parameter 'top_n' harus berupa angka bulat."

    if value < minimum or value > maximum:
        return None, f"Parameter 'top_n' harus berada di rentang {minimum}-{maximum}."

    return value, None


class MLHealthCheckView(APIView):
    def get(self, request):
        is_ready = (
            RecommendationConfig.sim_matrix is not None and 
            RecommendationConfig.df_products is not None
        )

        if is_ready:
            logger.info(
                "Health check sukses. sim_matrix_shape=%s, reference_products=%s",
                RecommendationConfig.sim_matrix.shape,
                len(RecommendationConfig.df_products),
            )
            return Response(
                {
                    "status": "success",
                    "message": "Layanan ML sehat dan model berhasil dimuat.",
                    "details": {
                        "sim_matrix_shape": RecommendationConfig.sim_matrix.shape,
                        "reference_products_count": len(RecommendationConfig.df_products)
                    }
                },
                status=status.HTTP_200_OK
            )

        logger.error("Health check gagal karena artifacts belum tersedia.")
        return Response(
            {
                "status": "error",
                "message": "Layanan ML tidak tersedia. Gagal memuat artifacts."
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )

class ProductRecommendationView(APIView):
    def get(self, request, product_id):
        top_n, error = _resolve_top_n(request)
        if error:
            logger.warning(
                "Input top_n tidak valid pada endpoint produk. product_id=%s, top_n_raw=%s, client_ip=%s",
                product_id,
                request.query_params.get('top_n'),
                request.META.get('REMOTE_ADDR'),
            )
            return Response(
                {"status": "error", "message": error},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = RecommendationService.get_by_product(product_id, top_n)

        if "error" in result:
            log_msg = (
                "Gagal memproses rekomendasi produk. product_id=%s, top_n=%s, status=%s, message=%s"
            )
            if result["status"] >= 500:
                logger.error(log_msg, product_id, top_n, result["status"], result["error"])
            else:
                logger.warning(log_msg, product_id, top_n, result["status"], result["error"])
            return Response(
                {"status": "error", "message": result["error"]}, 
                status=result["status"]
            )

        logger.info(
            "Endpoint rekomendasi produk sukses. product_id=%s, top_n=%s, result_count=%s",
            product_id,
            top_n,
            len(result["data"]),
        )
        return Response(
            {"status": "success", "data": result["data"]}, 
            status=status.HTTP_200_OK
        )

class EventRecommendationView(APIView):
    def get(self, request, event_type):
        top_n, error = _resolve_top_n(request)
        if error:
            logger.warning(
                "Input top_n tidak valid pada endpoint event. event_type=%s, top_n_raw=%s, client_ip=%s",
                event_type,
                request.query_params.get('top_n'),
                request.META.get('REMOTE_ADDR'),
            )
            return Response(
                {"status": "error", "message": error},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = RecommendationService.get_by_event(event_type, top_n)

        if "error" in result:
            log_msg = (
                "Gagal memproses rekomendasi event. event_type=%s, top_n=%s, status=%s, message=%s"
            )
            if result["status"] >= 500:
                logger.error(log_msg, event_type, top_n, result["status"], result["error"])
            else:
                logger.warning(log_msg, event_type, top_n, result["status"], result["error"])
            return Response(
                {"status": "error", "message": result["error"]}, 
                status=result["status"]
            )
        
        logger.info(
            "Endpoint rekomendasi event sukses. event_type=%s, top_n=%s, result_count=%s",
            event_type,
            top_n,
            len(result["data"]),
        )
        return Response(
            {"status": "success", "data": result["data"]}, 
            status=status.HTTP_200_OK
        )