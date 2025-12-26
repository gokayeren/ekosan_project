#!/bin/bash

# Hata olursa dur
set -e

echo "--- EKOSAN SİSTEM KURULUMU BAŞLATILIYOR ---"

# 1. Github'dan güncel kodları çek
echo ">>> Git Pull yapılıyor..."
git pull origin main

# 2. Sistemdeki tüm servisleri ayağa kaldır
# --build: Python kodunda değişiklik varsa yeniden derler.
# Nginx Proxy Manager hazır image olduğu için onu tekrar derlemez, sadece başlatır.
echo ">>> Docker Servisleri Başlatılıyor (App + DB + NPM)..."
docker compose up -d --build --remove-orphans

# 3. Gereksiz imaj temizliği
echo ">>> Temizlik yapılıyor..."
docker image prune -f

echo "--- İŞLEM TAMAMLANDI ---"
echo "Nginx Proxy Manager Paneli: http://SUNUCU_IP_ADRESI:81"
echo "Giriş Bilgileri (Varsayılan): admin@example.com / changeme"