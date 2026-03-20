from django.apps import AppConfig
import joblib
import os
import pandas as pd
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class RecommendationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recommendation'

    sim_matrix = None
    df_products = None
    artifacts_loaded = False

    def ready(self):
        if type(self).artifacts_loaded:
            logger.debug("Inisialisasi artifacts dilewati karena sudah dimuat sebelumnya.")
            return

        artifact_dir = os.path.join(settings.BASE_DIR, 'ml_artifacts')
        sim_matrix_path = os.path.join(artifact_dir, 'cosine_sim_matrix.joblib')
        products_path = os.path.join(artifact_dir, 'df_products_reference.pkl')

        try:
            type(self).sim_matrix = joblib.load(sim_matrix_path)
            type(self).df_products = pd.read_pickle(products_path)
            type(self).artifacts_loaded = True
            logger.info(
                "ML artifacts berhasil dimuat. sim_matrix_shape=%s, reference_products=%s",
                getattr(type(self).sim_matrix, "shape", None),
                len(type(self).df_products),
            )
        except Exception as e:
            logger.exception(
                "Gagal memuat ML artifacts dari disk. sim_matrix_path=%s, products_path=%s, err=%s",
                sim_matrix_path,
                products_path,
                str(e),
            )