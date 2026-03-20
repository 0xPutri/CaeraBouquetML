from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import logging
from .services import RecommendationService
from .apps import RecommendationConfig

logger = logging.getLogger(__name__)


def _sanitize_for_log(value, max_len: int = 100) -> str:
    """Membersihkan nilai untuk logging agar aman dari injeksi baris log."""
    sanitized = str(value).replace('\n', ' ').replace('\r', ' ').strip()
    return sanitized[:max_len]


def _resolve_top_n(request, default: int = 5, minimum: int = 1, maximum: int = 20):
    """
    Memvalidasi parameter top_n dari query endpoint rekomendasi.

    Fungsi ini menjaga agar jumlah rekomendasi tetap dalam rentang aman
    sehingga layanan stabil saat menerima berbagai jenis input.

    Args:
        request (Request): Objek request yang membawa query parameter.
        default (int): Nilai bawaan saat top_n tidak dikirim.
        minimum (int): Batas nilai minimum top_n.
        maximum (int): Batas nilai maksimum top_n.

    Returns:
        tuple[int | None, str | None]: Nilai top_n valid atau pesan error.
    """
    raw_top_n = request.query_params.get('top_n', default)
    try:
        value = int(raw_top_n)
    except (TypeError, ValueError):
        return None, "Parameter 'top_n' harus berupa angka bulat."

    if value < minimum or value > maximum:
        return None, f"Parameter 'top_n' harus berada di rentang {minimum}-{maximum}."

    return value, None


class MLHealthCheckView(APIView):
    """
    Menyediakan endpoint health check untuk modul ML recommendation.

    Endpoint ini membantu monitoring kesiapan artifacts sebelum
    frontend meminta rekomendasi bouquet.
    """

    def get(self, request):
        """
        Mengembalikan status kesiapan layanan machine learning.

        Args:
            request (Request): Objek request dari klien.

        Returns:
            Response: Respons sukses jika artifacts siap, selain itu error 503.
        """
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
    """
    Menangani permintaan rekomendasi berdasarkan produk acuan.

    Endpoint ini dipakai saat pengguna melihat satu bouquet dan
    membutuhkan daftar produk lain yang paling mirip.
    """

    def get(self, request, product_id):
        """
        Memproses request rekomendasi produk berbasis similarity.

        Args:
            request (Request): Objek request yang memuat query top_n.
            product_id (str): ID produk bouquet yang sedang dilihat pengguna.

        Returns:
            Response: Respons rekomendasi produk atau pesan error.
        """
        safe_product_id = _sanitize_for_log(product_id)
        safe_top_n_raw = _sanitize_for_log(request.query_params.get('top_n'))
        safe_client_ip = _sanitize_for_log(request.META.get('REMOTE_ADDR'))
        top_n, error = _resolve_top_n(request)
        if error:
            logger.warning(
                "Input top_n tidak valid pada endpoint produk. product_id=%s, top_n_raw=%s, client_ip=%s",
                safe_product_id,
                safe_top_n_raw,
                safe_client_ip,
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
            safe_error_message = _sanitize_for_log(result["error"], max_len=200)
            if result["status"] >= 500:
                logger.error(log_msg, safe_product_id, top_n, result["status"], safe_error_message)
            else:
                logger.warning(log_msg, safe_product_id, top_n, result["status"], safe_error_message)
            return Response(
                {"status": "error", "message": result["error"]}, 
                status=result["status"]
            )

        logger.info(
            "Endpoint rekomendasi produk sukses. product_id=%s, top_n=%s, result_count=%s",
            safe_product_id,
            top_n,
            len(result["data"]),
        )
        return Response(
            {"status": "success", "data": result["data"]}, 
            status=status.HTTP_200_OK
        )

class EventRecommendationView(APIView):
    """
    Menangani permintaan rekomendasi berdasarkan kategori acara.

    Endpoint ini membantu pengguna menemukan bouquet yang relevan
    untuk momen seperti graduation, birthday, atau wedding.
    """

    def get(self, request, event_type):
        """
        Memproses request rekomendasi produk berbasis event_type.

        Args:
            request (Request): Objek request yang memuat query top_n.
            event_type (str): Jenis acara yang menjadi konteks rekomendasi.

        Returns:
            Response: Respons rekomendasi event atau pesan error.
        """
        safe_event_type = _sanitize_for_log(event_type)
        safe_top_n_raw = _sanitize_for_log(request.query_params.get('top_n'))
        safe_client_ip = _sanitize_for_log(request.META.get('REMOTE_ADDR'))
        top_n, error = _resolve_top_n(request)
        if error:
            logger.warning(
                "Input top_n tidak valid pada endpoint event. event_type=%s, top_n_raw=%s, client_ip=%s",
                safe_event_type,
                safe_top_n_raw,
                safe_client_ip,
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
            safe_error_message = _sanitize_for_log(result["error"], max_len=200)
            if result["status"] >= 500:
                logger.error(log_msg, safe_event_type, top_n, result["status"], safe_error_message)
            else:
                logger.warning(log_msg, safe_event_type, top_n, result["status"], safe_error_message)
            return Response(
                {"status": "error", "message": result["error"]}, 
                status=result["status"]
            )
        
        logger.info(
            "Endpoint rekomendasi event sukses. event_type=%s, top_n=%s, result_count=%s",
            safe_event_type,
            top_n,
            len(result["data"]),
        )
        return Response(
            {"status": "success", "data": result["data"]}, 
            status=status.HTTP_200_OK
        )