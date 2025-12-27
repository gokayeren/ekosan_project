# 1. Base Image: Python 3.10'un hafif sürümü (slim)
FROM python:3.10-slim

# 2. Çalışma dizini
WORKDIR /app

# 3. Sistem Bağımlılıkları
# gcc & libpq-dev: PostgreSQL bağlantısı (psycopg2) için zorunlu.
# libjpeg-dev & zlib1g-dev: Pillow (resim yükleme/işleme) için zorunlu.
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# 4. Python Paketleri
# Önce sadece requirements kopyalanır (Docker cache mekanizması için önemli)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Gunicorn requirements.txt içinde yoksa buradan kurulur
RUN pip install gunicorn

# 5. Kodun Kopyalanması
COPY . .

# 6. Ortam Değişkenleri
ENV FLASK_APP=run.py
ENV FLASK_DEBUG=0
# Python çıktılarının loglara anlık düşmesi için:
ENV PYTHONUNBUFFERED=1 

# 7. Port (Bilgi amaçlı, asıl yönlendirmeyi docker-compose yapar)
EXPOSE 5000

# 8. Başlatma Komutu
# sh -c ile zincirleme komut çalıştırıyoruz.
# flask db upgrade: Veritabanı tablolarını oluşturur/günceller.
# gunicorn: Uygulamayı başlatır. "-w 4" 4 işçi çalıştırır (Performans için).
CMD ["sh", "-c", "flask db upgrade && gunicorn -w 4 --bind 0.0.0.0:5000 run:app"]