#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_DIR}"

BACKUP_DIR="${BACKUP_DIR:-${PROJECT_DIR}/backups}"
BACKUP_KEEP_COUNT="${BACKUP_KEEP_COUNT:-7}"
TIMESTAMP="$(date -u +'%Y%m%d_%H%M%S')"
DB_FINAL="${BACKUP_DIR}/db_${TIMESTAMP}.dump"
DB_TEMP="${DB_FINAL}.tmp"
UPLOAD_FINAL="${BACKUP_DIR}/uploads_${TIMESTAMP}.tar.gz"
UPLOAD_TEMP="${UPLOAD_FINAL}.tmp"

case "${BACKUP_KEEP_COUNT}" in
    ''|*[!0-9]*)
        echo "HATA: BACKUP_KEEP_COUNT pozitif bir tam sayı olmalıdır." >&2
        exit 1
        ;;
esac

if [ "${BACKUP_KEEP_COUNT}" -lt 1 ]; then
    echo "HATA: En az 1 yedek tutulmalıdır." >&2
    exit 1
fi

mkdir -p -- "${BACKUP_DIR}"

cleanup_temp_files() {
    rm -f -- "${DB_TEMP}" "${UPLOAD_TEMP}"
}
trap cleanup_temp_files EXIT

wait_for_database() {
    local attempt
    for attempt in $(seq 1 30); do
        if docker compose exec -T db sh -c \
            'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"' >/dev/null 2>&1; then
            return 0
        fi
        sleep 2
    done

    echo "HATA: Veritabanı 60 saniye içinde hazır olmadı." >&2
    return 1
}

trim_backups() {
    local prefix="$1"
    local suffix="$2"
    local files=()
    local remove_count=0
    local index=0

    shopt -s nullglob
    files=("${BACKUP_DIR}/${prefix}"_*".${suffix}")
    shopt -u nullglob

    if [ "${#files[@]}" -le "${BACKUP_KEEP_COUNT}" ]; then
        return 0
    fi

    # Zaman damgalı adlar alfabetik olarak eskiden yeniye sıralanır.
    remove_count=$(("${#files[@]}" - BACKUP_KEEP_COUNT))
    for ((index = 0; index < remove_count; index++)); do
        echo "Eski yedek siliniyor: ${files[$index]}"
        rm -f -- "${files[$index]}"
    done
}

echo "Veritabanı servisi hazırlanıyor..."
docker compose up -d db
wait_for_database

echo "PostgreSQL yedeği alınıyor..."
docker compose exec -T db sh -c \
    'exec pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --format=custom --compress=6' \
    >"${DB_TEMP}"

if [ ! -s "${DB_TEMP}" ]; then
    echo "HATA: Veritabanı yedeği boş oluştu." >&2
    exit 1
fi

if ! docker compose exec -T db pg_restore --list <"${DB_TEMP}" >/dev/null; then
    echo "HATA: Veritabanı yedeği doğrulanamadı." >&2
    exit 1
fi

echo "Yüklenen medya dosyaları yedekleniyor..."
if [ -z "$(docker compose images -q app 2>/dev/null)" ]; then
    echo "HATA: Medya volume'una erişmek için mevcut uygulama imajı bulunamadı." >&2
    exit 1
fi

docker compose run -T --rm --no-deps --entrypoint sh app -c \
    'exec tar -czf - -C /app/app/static/uploads .' >"${UPLOAD_TEMP}"

if [ ! -s "${UPLOAD_TEMP}" ] || ! tar -tzf "${UPLOAD_TEMP}" >/dev/null; then
    echo "HATA: Medya yedeği doğrulanamadı." >&2
    exit 1
fi

# İki yedek de doğrulandıktan sonra birlikte kalıcı adlarına geçirilir.
mv -- "${DB_TEMP}" "${DB_FINAL}"
mv -- "${UPLOAD_TEMP}" "${UPLOAD_FINAL}"

trim_backups "db" "dump"
trim_backups "uploads" "tar.gz"

# Yalnızca bu klasörde yarım kalmış, bir günden eski geçici yedekleri temizler.
find "${BACKUP_DIR}" -maxdepth 1 -type f -name '*.tmp' -mtime +1 -delete

echo "Yedekleme tamamlandı:"
echo "  ${DB_FINAL}"
echo "  ${UPLOAD_FINAL}"
echo "Tutulan azami yedek sayısı: ${BACKUP_KEEP_COUNT}"
du -sh -- "${BACKUP_DIR}" 2>/dev/null || true
