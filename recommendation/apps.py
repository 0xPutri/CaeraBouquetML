from django.apps import AppConfig
import joblib
import os
import pandas as pd
from django.conf import settings

class RecommendationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recommendation'

    sim_matrix = None
    df_products = None
    artifacts_loaded = False

    def ready(self):
        if type(self).artifacts_loaded:
            return

        artifact_dir = os.path.join(settings.BASE_DIR, 'ml_artifacts')

        try:
            type(self).sim_matrix = joblib.load(
                os.path.join(artifact_dir, 'cosine_sim_matrix.joblib')
            )
            type(self).df_products = pd.read_pickle(
                os.path.join(artifact_dir, 'df_products_reference.pkl')
            )
            type(self).artifacts_loaded = True
            print("[INFO] ML Artifacts berhasil dimuat ke dalam memori.")
        except Exception as e:
            print(f"[ERROR] Gagal memuat ML Artifacts: {e}")