# CaeraBouquet ML Service

Layanan ini adalah backend **Machine Learning Recommendation API** untuk CaeraBouquet.
Sistem berfokus pada rekomendasi bouquet berbasis **Content-Based Filtering** dengan **Cosine Similarity** melalui dua skenario utama: kemiripan produk dan kategori acara.

## Ringkasan Sistem

- Pipeline inti: data retrieval, feature preparation, encoding, similarity calculation, dan recommendation generation.
- Tujuan: membantu pengguna memilih produk bouquet melalui rekomendasi yang relevan.
- Ruang lingkup: preprocessing fitur produk, perhitungan similarity, dan penyajian hasil melalui API.
- Fitur utama model: `product_type`, `product_theme`, `event_type`, `size`, `price`, `popularity`.

## Instalasi

1. **Clone repository**
   
   ```bash
   git clone https://github.com/0xPutri/CaeraBouquetML.git
   cd CaeraBouquetML
   ```

2. **Setup environment**
   
   ```bash
   pip install -r requirements.txt
   cp .env.example .env
   ```

3. **Jalankan aplikasi**
   
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

## API Endpoint

| Endpoint | Method | Parameter | Deskripsi Singkat | Respons Utama |
|---|---|---|---|---|
| `/health/` | `GET` | - | Memeriksa kesiapan artifacts model di memori. | `200` siap, `503` belum siap |
| `/api/recommendations/product/<product_id>/` | `GET` | Query: `top_n` (opsional, default `5`, rentang `1-20`) | Rekomendasi produk paling mirip berdasarkan `product_id`. | `200` data rekomendasi, `404` produk tidak ditemukan, `500` error internal |
| `/api/recommendations/event/<event_type>/` | `GET` | Query: `top_n` (opsional, default `5`, rentang `1-20`) | Rekomendasi produk berdasarkan kategori acara (`event_type`). | `200` data rekomendasi, `404` event tidak ditemukan, `500` error internal |

## Catatan

Model menggunakan artifacts lokal di folder `ml_artifacts` saat startup, parameter `top_n` dibatasi `1-20`, endpoint `/health/` untuk cek kesiapan model, dan data rekomendasi memakai dataset sintetis untuk kebutuhan uji/integrasi.

## Lisensi

Proyek ini menggunakan lisensi **MIT**. Lihat detail lengkap pada file [`LICENSE`](LICENSE).