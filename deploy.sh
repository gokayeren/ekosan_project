#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

DEPLOY_BRANCH="${DEPLOY_BRANCH:-main}"
IMAGE_PRUNE_AGE="${IMAGE_PRUNE_AGE:-168h}"
DEPLOY_CONTINUE="${EKOSAN_DEPLOY_CONTINUE:-0}"

if ! command -v git >/dev/null 2>&1; then
    echo "HATA: git bulunamadı." >&2
    exit 1
fi

if ! command -v docker >/dev/null 2>&1 || ! docker compose version >/dev/null 2>&1; then
    echo "HATA: Docker Compose bulunamadı." >&2
    exit 1
fi

if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "HATA: Sunucuda commit edilmemiş takipli dosya değişiklikleri var." >&2
    echo "Güncellemeden önce 'git status' ile kontrol edin." >&2
    exit 1
fi

if [ "${DEPLOY_CONTINUE}" != "1" ]; then
    if command -v flock >/dev/null 2>&1; then
        exec 9>"${SCRIPT_DIR}/.deploy.lock"
        if ! flock -n 9; then
            echo "HATA: Bu proje için başka bir deploy işlemi devam ediyor." >&2
            exit 1
        fi
    fi

    echo ">>> Güncelleme öncesi doğrulanmış yedek alınıyor..."
    bash "${SCRIPT_DIR}/scripts/backup.sh"

    echo ">>> GitHub güncellemeleri çekiliyor..."
    git fetch origin "${DEPLOY_BRANCH}"
    git merge --ff-only "origin/${DEPLOY_BRANCH}"

    # deploy.sh pull sırasında değişmiş olsa bile kalan adımlar yeni dosyayla çalışır.
    export EKOSAN_DEPLOY_CONTINUE=1
    exec bash "${SCRIPT_DIR}/deploy.sh"
fi
unset EKOSAN_DEPLOY_CONTINUE

echo ">>> Yeni uygulama imajı hazırlanıyor..."
docker compose build app

echo ">>> Veritabanı ve proxy servisleri hazırlanıyor..."
docker compose up -d db nginx_proxy

echo ">>> Veritabanı migration işlemi kontrollü olarak çalıştırılıyor..."
docker compose run --rm --no-deps app flask db upgrade

echo ">>> Uygulama yeni sürümle başlatılıyor..."
docker compose up -d --no-deps app
docker compose up -d --remove-orphans

echo ">>> Uygulama sağlık kontrolü bekleniyor..."
APP_CONTAINER_ID="$(docker compose ps -q app)"
if [ -z "${APP_CONTAINER_ID}" ]; then
    echo "HATA: Uygulama container'ı bulunamadı." >&2
    exit 1
fi

for attempt in $(seq 1 30); do
    APP_HEALTH="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "${APP_CONTAINER_ID}")"
    if [ "${APP_HEALTH}" = "healthy" ]; then
        break
    fi
    if [ "${APP_HEALTH}" = "unhealthy" ] || [ "${APP_HEALTH}" = "exited" ]; then
        echo "HATA: Uygulama sağlıklı başlamadı (${APP_HEALTH})." >&2
        docker compose logs --tail=100 app
        exit 1
    fi
    sleep 2
done

APP_HEALTH="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "${APP_CONTAINER_ID}")"
if [ "${APP_HEALTH}" != "healthy" ]; then
    echo "HATA: Uygulama sağlık kontrolü zaman aşımına uğradı (${APP_HEALTH})." >&2
    docker compose logs --tail=100 app
    exit 1
fi

echo ">>> Yalnızca kullanılmayan ve 7 günden eski Docker imajları temizleniyor..."
docker image prune -f --filter "until=${IMAGE_PRUNE_AGE}"
echo ">>> Yalnızca kullanılmayan ve 7 günden eski Docker build önbelleği temizleniyor..."
docker builder prune -f --filter "until=${IMAGE_PRUNE_AGE}"

echo "--- GÜVENLİ GÜNCELLEME TAMAMLANDI ---"
echo "Nginx Proxy Manager Paneli: http://SUNUCU_IP_ADRESI:81"
echo ""
echo "Admin Paneli"
echo "Yeni Admin Ekle : docker exec -it ekosan_app_v2 flask create-admin \"kullanici_adi\" \"sifre\""
echo "Admin Sil       : docker exec -it ekosan_app_v2 flask delete-admin \"kullanici_adi\""
echo "Adminleri Gör   : docker exec -it ekosan_app_v2 flask list-admins"
echo "-----------------------------------------------"
