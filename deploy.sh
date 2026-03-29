#!/bin/bash
set -e
echo ">>> Git Pull yapılıyor..."
git pull origin main

echo ">>> Docker Servisleri Başlatılıyor (App + DB + NPM)..."
docker compose up -d --build --remove-orphans

echo ">>> Temizlik yapılıyor..."
docker image prune -f

echo "--- İŞLEM TAMAMLANDI ---"
echo "Nginx Proxy Manager Paneli: http://SUNUCU_IP_ADRESI:81"
echo ""
echo "Admin Paneli"
echo "Yeni Admin Ekle : docker exec -it ekosan_app_v2 flask create-admin \"kullanici_adi\" \"sifre\""
echo "Admin Sil       : docker exec -it ekosan_app_v2 flask delete-admin \"kullanici_adi\""
echo "Adminleri Gör   : docker exec -it ekosan_app_v2 flask list-admins"
echo "-----------------------------------------------"