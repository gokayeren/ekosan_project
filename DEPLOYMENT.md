# Güvenli sunucu güncellemesi

Bu yapı PostgreSQL verisini, admin panelinden yüklenen medyaları ve SSL/proxy
ayarlarını uygulama kodundan ayrı tutar.

## İlk geçiş

Sunucu eski `deploy.sh` dosyasını kullanıyorsa yeni sistemi ilk kez almak için
yalnızca kodu çekin; bu komut container veya volume'lara dokunmaz:

```bash
git pull --ff-only origin main
bash deploy.sh
```

Sonraki güncellemelerde tek komut yeterlidir:

```bash
bash deploy.sh
```

## Stil dosyasını güncelleme

Tailwind ve DaisyUI tarayıcıda derlenmez; performans için üretim CSS'i projede
önceden oluşturulur. Şablonlarda yeni Tailwind sınıfları kullanıldığında,
değişiklik GitHub'a gönderilmeden önce:

```bash
python -m pip install -r requirements-dev.txt
pnpm install --frozen-lockfile
pnpm run build:css
python scripts/build_icon_subset.py
python scripts/build_vendor_assets.py
```

Üretilen `app/static/css/site.min.css`, `app/static/css/icons.min.css`,
`app/static/fonts/` ve `app/static/vendor/` dosyaları kodla birlikte commit edilir.
Sunucunun Node.js veya pnpm kurmasına gerek yoktur.

Deploy sırasıyla şunları yapar:

1. PostgreSQL ve yüklenen medya dosyalarının yedeğini alır.
2. Her iki yedeği de açılabilirlik açısından doğrular.
3. GitHub'dan yalnızca fast-forward güncellemesini kabul eder.
4. Yeni uygulama imajını oluşturur.
5. Veritabanı migration işlemini ayrı ve kontrollü çalıştırır.
6. Uygulamayı başlatıp sağlık kontrolünü bekler.
7. Eski yedekleri ve kullanılmayan eski Docker katmanlarını sınırlar.

Aynı proje için iki deploy aynı anda başlatılırsa, sunucuda `flock` bulunduğu
sürece ikinci işlem güvenli biçimde durdurulur.

## Yedek saklama sınırı

Varsayılan olarak son **7 veritabanı** ve son **7 medya** yedeği tutulur.
Sunucuda başka bir sınır kullanmak için:

```bash
BACKUP_KEEP_COUNT=5 bash deploy.sh
```

Yedekler proje içindeki `backups/` klasörüne yazılır. Bu klasör GitHub'a
gönderilmez ve Docker imajına dahil edilmez.

Tek başına manuel yedek almak için:

```bash
bash scripts/backup.sh
```

## Temizlik kapsamı

Otomatik temizlik yalnızca aşağıdakileri siler:

- `backups/db_*.dump` desenindeki sınırı aşan eski yedekler
- `backups/uploads_*.tar.gz` desenindeki sınırı aşan eski yedekler
- `backups/*.tmp` desenindeki bir günden eski yarım dosyalar
- hiçbir container tarafından kullanılmayan, 7 günden eski dangling Docker imajları
- kullanılmayan ve 7 günden eski Docker build önbelleği

PostgreSQL volume'u, medya volume'u, `npm_data` ve `npm_letsencrypt`
klasörleri hiçbir temizlik komutunun hedefi değildir.

> `docker compose down -v` çalıştırmayın. `-v` seçeneği canlı veritabanı ve
> medya volume'larını silebilir.

## Ayarlanabilir değerler

```bash
# Farklı branch
DEPLOY_BRANCH=main bash deploy.sh

# Docker temizliğini 14 güne çıkar
IMAGE_PRUNE_AGE=336h bash deploy.sh

# Yedekleri başka bir diskte sakla
BACKUP_DIR=/mnt/backup/ekosan BACKUP_KEEP_COUNT=7 bash deploy.sh
```

`BACKUP_DIR` proje dışına alınacaksa hedef klasörün yalnızca yetkili kullanıcı
tarafından erişilebilir olması önerilir.
