import numpy as np
from .apps import RecommendationConfig

class RecommendationService:

    @staticmethod
    def get_by_product(product_id: str, top_n: int = 5) -> dict:
        df = RecommendationConfig.df_products
        sim_matrix = RecommendationConfig.sim_matrix

        if df is None or sim_matrix is None:
            return {
                "error": "Model artifacts belum siap/tidak termuat.",
                "status": 500
            }
        
        if product_id not in df['product_id'].values:
            return {
                "error": f"Produk dengan ID '{product_id}' tidak ditemukan.",
                "status": 404
            }
        
        idx = df.index[df['product_id'] == product_id].tolist()[0]
        sim_scores = list(enumerate(sim_matrix[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        top_items = sim_scores[1:top_n+1]

        product_indices = [i[0] for i in top_items]
        scores = [i[1] for i in top_items]

        result_df = df.iloc[product_indices][['product_id', 'product_type', 'event_type', 'price', 'tags']].copy()
        result_df['similarity_score'] = np.round(scores, 2)

        return {
            "data": result_df.to_dict('records'),
            "status": 200
        }
    
    @staticmethod
    def get_by_event(event_type: str, top_n: int = 5) -> dict:
        df = RecommendationConfig.df_products

        if df is None:
            return {
                "error": "Model artifacts belum siap/tidak termuat.",
                "status": 500
            }
        
        filtered_df = df[df['event_type'].str.lower() == event_type.lower()].copy()

        if filtered_df.empty:
            return {
               "error": f"Tidak ditemukan produk untuk acara '{event_type}'.",
               "status": 404 
            }
        
        result_df = filtered_df.head(top_n)[['product_id', 'product_type', 'event_type', 'price', 'tags']]
        return {
            "data": result_df.to_dict('records'),
            "status": 200
        }