import requests
import json
import os
import smtplib
import hashlib
import uuid
from pathlib import Path
from datetime import datetime
from email.message import EmailMessage
from xml.sax.saxutils import escape as xml_escape
from urllib.parse import urlsplit
from flask import render_template, request, redirect, url_for, flash, current_app, abort, send_file, Response
from PIL import Image, ImageOps, UnidentifiedImageError
from app import db
from app.main import main
from app.models import (
    HomeConfig, Corporate, References, Contact, Getoffer,
    Service, Form, FormSubmission, SiteSetting
)

def get_shared_data():
    home_config = HomeConfig.query.first() or HomeConfig()
    services = Service.query.filter_by(is_active=True).order_by(Service.order.asc()).all()
    return home_config, services


def get_canonical_root():
    settings = SiteSetting.query.first()
    configured_url = settings.seo_canonical_url if settings else None
    return (configured_url or 'https://ekosanmuhendislik.com').rstrip('/')


@main.before_request
def redirect_public_aliases_to_canonical():
    """Consolidate www and secondary domains without breaking local health checks."""
    canonical_root = get_canonical_root()
    canonical_parts = urlsplit(canonical_root)
    current_host = (request.host.split(':', 1)[0] or '').lower()
    canonical_host = (canonical_parts.hostname or '').lower()
    local_hosts = {'127.0.0.1', 'localhost', '::1'}

    if (
        request.method in ('GET', 'HEAD')
        and current_host
        and canonical_host
        and current_host not in local_hosts
        and current_host != canonical_host
    ):
        target = f'{canonical_root}{request.path}'
        if request.query_string:
            target = f'{target}?{request.query_string.decode("utf-8", errors="ignore")}'
        return redirect(target, code=301)


@main.after_request
def apply_public_seo_headers(response):
    """Mirror page-level noindex rules in the HTTP headers."""
    try:
        settings = SiteSetting.query.first()
        homepage_only = settings.seo_homepage_only if settings else True
        is_html = response.content_type and response.content_type.startswith('text/html')
        if homepage_only and request.endpoint != 'main.index' and is_html:
            response.headers['X-Robots-Tag'] = 'noindex, follow'
    except Exception:
        pass
    return response


@main.route('/robots.txt')
def robots_txt():
    canonical_root = get_canonical_root()
    content = "\n".join([
        'User-agent: *',
        'Allow: /',
        'Disallow: /admin/',
        'Disallow: /login',
        'Disallow: /logout',
        'Disallow: /form-submit',
        '',
        f'Sitemap: {canonical_root}/sitemap.xml',
        ''
    ])
    return Response(content, mimetype='text/plain')


@main.route('/sitemap.xml')
def sitemap_xml():
    settings = SiteSetting.query.first()
    canonical_root = get_canonical_root()
    urls = [f'{canonical_root}/']

    if settings and not settings.seo_homepage_only:
        urls.extend([
            f'{canonical_root}/kurumsal',
            f'{canonical_root}/referanslar',
            f'{canonical_root}/iletisim',
            f'{canonical_root}/teklifal'
        ])
        urls.extend(
            f'{canonical_root}/hizmetler/{service.slug}'
            for service in Service.query.filter_by(is_active=True).all()
        )

    entries = ''.join(
        f'<url><loc>{xml_escape(url)}</loc></url>'
        for url in urls
    )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f'{entries}</urlset>'
    )
    return Response(xml, mimetype='application/xml')


@main.route('/llms.txt')
def llms_txt():
    settings = SiteSetting.query.first() or SiteSetting()
    services = Service.query.filter_by(is_active=True).order_by(Service.order.asc()).all()
    lines = [
        '# Ekosan Isı',
        '',
        settings.seo_default_description or 'Kdz. Ereğli merkezli ısıtma, soğutma ve enerji çözümleri firması.',
        '',
        '## Temel bilgiler',
        f'- Resmî site: {get_canonical_root()}/',
        f'- Telefon: {settings.phone_number or "03723124838"}',
        f'- E-posta: {settings.email_address or "bilgi@ekosanmuhendislik.com"}',
        f'- Adres: {settings.address or "Karadeniz Ereğli, Zonguldak"}',
        '',
        '## Hizmetler'
    ]
    for service in services:
        summary = service.short_description or service.subtitle or ''
        lines.append(f'- {service.title}: {summary}'.rstrip())
    lines.extend(['', 'Bu dosya yapay zekâ sistemlerinin firma bilgilerini doğru yorumlamasına yardımcı olmak için hazırlanmıştır.', ''])
    response = Response('\n'.join(lines), mimetype='text/plain')
    response.headers['X-Robots-Tag'] = 'noindex'
    return response


def send_submission_notification(target_email, subject, body, reply_to=None, form_data=None):
    """Send a form notification through the configured provider."""
    settings = SiteSetting.query.first()
    provider = settings.form_notification_provider if settings else 'formsubmit'

    if provider != 'smtp':
        payload = {
            '_subject': subject,
            '_captcha': 'false',
            '_template': 'box',
        }
        if reply_to:
            payload['_replyto'] = reply_to
        payload.update(form_data or {'Mesaj': body})
        response = requests.post(
            f"https://formsubmit.co/ajax/{target_email}",
            data=payload,
            headers={
                'User-Agent': 'Ekosan-Flask-App',
                'Accept': 'application/json',
                'Referer': request.url,
            },
            timeout=10,
        )
        if response.status_code not in (200, 201):
            raise RuntimeError(f'FormSubmit isteği başarısız ({response.status_code}).')
        return 'formsubmit_submitted'

    smtp_host = settings.smtp_host
    smtp_user = settings.smtp_user
    smtp_pass = settings.smtp_password
    smtp_port = settings.smtp_port or 587
    smtp_from = settings.smtp_from or smtp_user
    smtp_use_ssl = bool(settings.smtp_use_ssl)

    if not all((smtp_host, smtp_user, smtp_pass, smtp_from)):
        raise RuntimeError('SMTP ayarları panelden tamamlanmalı.')

    message = EmailMessage()
    message['Subject'] = subject
    message['From'] = smtp_from
    message['To'] = target_email
    if reply_to:
        message['Reply-To'] = reply_to
    message.set_content(body)

    smtp_class = smtplib.SMTP_SSL if smtp_use_ssl else smtplib.SMTP
    with smtp_class(smtp_host, smtp_port, timeout=15) as smtp:
        if not smtp_use_ssl:
            smtp.starttls()
        smtp.login(smtp_user, smtp_pass)
        smtp.send_message(message)
    return 'sent'


@main.route("/media/<path:filename>")
def optimized_media(filename):
    """Serve a cached WebP derivative without modifying the uploaded original."""
    upload_root = (Path(current_app.static_folder) / "uploads").resolve()
    source_path = (upload_root / filename).resolve()

    try:
        source_path.relative_to(upload_root)
    except ValueError:
        abort(404)

    if not source_path.is_file():
        abort(404)

    allowed_widths = (240, 480, 768, 1200, 1600)
    try:
        requested_width = int(request.args.get("w", 1200))
    except (TypeError, ValueError):
        requested_width = 1200
    target_width = min(allowed_widths, key=lambda width: abs(width - requested_width))

    source_stat = source_path.stat()
    webp_quality = 74
    cache_key = hashlib.sha256(
        f"{source_path.name}:{source_stat.st_mtime_ns}:{source_stat.st_size}:{target_width}:q{webp_quality}".encode()
    ).hexdigest()[:24]
    cache_dir = upload_root / ".optimized"
    cache_path = cache_dir / f"{cache_key}.webp"

    if not cache_path.exists():
        cache_dir.mkdir(parents=True, exist_ok=True)
        temp_path = cache_dir / f".{cache_key}-{uuid.uuid4().hex}.tmp"
        try:
            with Image.open(source_path) as source_image:
                optimized_image = ImageOps.exif_transpose(source_image)
                if optimized_image.width > target_width:
                    target_height = max(1, round(optimized_image.height * target_width / optimized_image.width))
                    optimized_image = optimized_image.resize(
                        (target_width, target_height),
                        Image.Resampling.LANCZOS
                    )

                if optimized_image.mode not in ("RGB", "RGBA"):
                    optimized_image = optimized_image.convert("RGBA" if "transparency" in optimized_image.info else "RGB")

                optimized_image.save(
                    temp_path,
                    format="WEBP",
                    quality=webp_quality,
                    method=4
                )
            os.replace(temp_path, cache_path)
        except (UnidentifiedImageError, OSError):
            if temp_path.exists():
                temp_path.unlink()
            response = send_file(source_path, conditional=True, max_age=86400)
            response.cache_control.public = True
            return response

    response = send_file(
        cache_path,
        mimetype="image/webp",
        conditional=True,
        max_age=31536000
    )
    response.cache_control.public = True
    response.cache_control.immutable = True
    return response

@main.route("/")
def index():
    home_config, services = get_shared_data()
    return render_template('index.html',
                           home_config=home_config,
                           services=services)

@main.route("/kurumsal")
def corporate():
    home_config, services = get_shared_data()
    corporate_data = Corporate.query.first() or Corporate()

    return render_template('corporate.html',
                           home_config=home_config,
                           corporate=corporate_data,
                           services=services)

@main.route("/referanslar")
def references():
    home_config, services = get_shared_data()

    references_data = References.query.first() or References()

    return render_template('references.html',
                           home_config=home_config,
                           references=references_data,
                           services=services)

@main.route("/iletisim")
def contact():
    home_config, services = get_shared_data()

    contact_data = Contact.query.first() or Contact()

    return render_template('contact.html',
                           home_config=home_config,
                           contact=contact_data,
                           services=services)

@main.route("/teklifal")
def getoffer():
    home_config, services = get_shared_data()
    contact_data = Contact.query.first() or Contact()
    
    getoffer_data = Getoffer.query.first() or Getoffer()

    return render_template('contact.html', 
                           home_config=home_config,
                           contact=contact_data,
                           getoffer=getoffer_data,
                           services=services)

@main.route("/hizmetler/<string:slug>")
def service_detail(slug):
    home_config, services = get_shared_data()
    service = Service.query.filter_by(slug=slug, is_active=True).first_or_404()
    canonical_root = get_canonical_root()
    schema_graph = [{
        '@type': 'Service',
        '@id': f'{canonical_root}/hizmetler/{service.slug}#service',
        'name': service.title,
        'description': service.meta_description or service.short_description or service.subtitle or '',
        'url': f'{canonical_root}/hizmetler/{service.slug}',
        'provider': {'@id': f'{canonical_root}/#business'},
        'areaServed': ['Karadeniz Ereğli', 'Alaplı', 'Akçakoca', 'Zonguldak']
    }]

    active_faqs = []
    if service.faq_group:
        active_faqs = [faq for faq in service.faq_group.items if faq.is_active]
    if active_faqs:
        schema_graph.append({
            '@type': 'FAQPage',
            'mainEntity': [{
                '@type': 'Question',
                'name': faq.question,
                'acceptedAnswer': {
                    '@type': 'Answer',
                    'text': faq.answer
                }
            } for faq in active_faqs]
        })

    service_schema = {
        '@context': 'https://schema.org',
        '@graph': schema_graph
    }

    return render_template('service_detail.html',
                           service=service,
                           service_schema=service_schema,
                           home_config=home_config,
                           services=services)

@main.route('/form-submit', methods=['POST'])
def submit_contact_form():
    form_id = request.form.get('form_id')

    if not request.form.get('kvkk'):
        flash('Lütfen KVKK aydınlatma metnini onaylayınız.', 'warning')
        return redirect(request.referrer or url_for('main.contact'))

    if not form_id:
        flash('Form tanımlayıcısı bulunamadı.', 'danger')
        return redirect(request.referrer or url_for('main.contact'))

    form_obj = Form.query.get(form_id)
    if not form_obj:
        flash('Geçersiz form.', 'danger')
        return redirect(request.referrer or url_for('main.contact'))

    try:
        data = {}
        for key in request.form:
            values = request.form.getlist(key)
            if len(values) > 1:
                data[key] = ", ".join(values)
            else:
                data[key] = values[0]

        data.pop('form_id', None)
        data.pop('kvkk', None)
        data.pop('csrf_token', None)

        json_data = json.dumps(data, ensure_ascii=False)
        submission = FormSubmission(
            form_id=form_id,
            submission_data=json_data,
            ip_address=request.remote_addr,
            notification_status='pending' if form_obj.recipient_email else 'not_configured'
        )

        db.session.add(submission)
        db.session.commit()

        if form_obj.recipient_email:
            try:
                target_email = form_obj.recipient_email
                subject = f"Yeni Mesaj: {form_obj.title} - {request.host}"
                body_lines = [f"{key}: {value}" for key, value in data.items()]
                body = "\n".join(body_lines)
                reply_to = None
                for key, value in data.items():
                    key_lower = key.lower()
                    if 'mail' in key_lower or 'e-posta' in key_lower or 'email' in key_lower:
                        reply_to = value
                        break

                notification_status = send_submission_notification(target_email, subject, body, reply_to, data)
                submission.notification_status = notification_status
                submission.notified_at = datetime.utcnow() if notification_status == 'sent' else None
                submission.notification_error = None
                db.session.commit()
                current_app.logger.info(f"Form notification submitted via {notification_status}: {target_email}")
                flash(form_obj.success_message or "Mesajınız başarıyla kaydedildi.", 'success')
                return redirect(request.referrer or url_for('main.contact'))

                smtp_host = os.environ.get('SMTP_HOST')
                smtp_user = os.environ.get('SMTP_USER')
                smtp_pass = os.environ.get('SMTP_PASSWORD')
                smtp_port = int(os.environ.get('SMTP_PORT', '587'))
                smtp_from = os.environ.get('SMTP_FROM') or smtp_user or target_email

                if smtp_host and smtp_user and smtp_pass:
                    msg = EmailMessage()
                    msg['Subject'] = subject
                    msg['From'] = smtp_from
                    msg['To'] = target_email
                    if reply_to:
                        msg['Reply-To'] = reply_to
                    msg.set_content(body)
                    with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as smtp:
                        smtp.starttls()
                        smtp.login(smtp_user, smtp_pass)
                        smtp.send_message(msg)
                    current_app.logger.info(f"SMTP mail başarıyla gönderildi: {target_email}")
                else:
                    payload = data.copy()
                    payload['_subject'] = subject
                    payload['_captcha'] = "false"
                    payload['_template'] = "box"
                    if reply_to:
                        payload['_replyto'] = reply_to
                    headers = {'User-Agent': 'Ekosan-Flask-App', 'Accept': 'application/json', 'Referer': request.url}
                    response = requests.post(f"https://formsubmit.co/ajax/{target_email}", data=payload, headers=headers, timeout=10)
                    if response.status_code in (200, 201):
                        current_app.logger.info(f"FormSubmit mail isteği başarılı: {target_email}")
                    else:
                        current_app.logger.error(f"Mail gönderme hatası ({response.status_code}): {response.text}")
            except Exception as mail_error:
                db.session.rollback()
                submission.notification_status = 'failed'
                submission.notification_error = str(mail_error)[:1000]
                db.session.add(submission)
                db.session.commit()
                current_app.logger.error(f"Mail sunucusu hatası: {mail_error}")
        
        success_msg = form_obj.success_message or "Mesajınız başarıyla iletildi."
        flash(success_msg, 'success')

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Form işlem hatası: {e}")
        flash('Bir hata oluştu, lütfen tekrar deneyiniz.', 'danger')

    return redirect(request.referrer or url_for('main.contact'))
