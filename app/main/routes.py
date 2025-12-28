import requests
import json
from flask import render_template, request, redirect, url_for, flash, current_app, abort
from app import db
from app.main import main
# Product modelini buraya ekledik
from app.models import (
    HomeConfig, Corporate, References, Contact, Getoffer,
    Service, Form, FormSubmission, Product
)

@main.route("/")
def index():
    home_config = HomeConfig.query.first()
    if not home_config:
        home_config = HomeConfig()

    # Hizmetleri menüde veya footerda göstermek için çekiyoruz
    services = Service.query.filter_by(is_active=True).order_by(Service.order.desc()).limit(6).all()

    return render_template('index.html',
                           home_config=home_config,
                           services=services)

@main.route("/kurumsal")
def corporate():
    home_config = HomeConfig.query.first() or HomeConfig()
    
    corporate_data = Corporate.query.first()
    if not corporate_data:
        corporate_data = Corporate() 

    services = Service.query.filter_by(is_active=True).order_by(Service.order.desc()).limit(6).all()

    return render_template('corporate.html',
                           home_config=home_config,
                           corporate=corporate_data,
                           services=services)

@main.route("/referanslar")
def references():
    home_config = HomeConfig.query.first() or HomeConfig()

    references_data = References.query.first()
    if not references_data:
        references_data = References() 

    services = Service.query.filter_by(is_active=True).order_by(Service.order.desc()).limit(6).all()

    return render_template('references.html',
                           home_config=home_config,
                           references=references_data,
                           services=services)

@main.route("/iletisim")
def contact():
    home_config = HomeConfig.query.first() or HomeConfig()

    contact_data = Contact.query.first()
    if not contact_data:
        contact_data = Contact()

    services = Service.query.filter_by(is_active=True).order_by(Service.order.desc()).limit(6).all()

    return render_template('contact.html',
                           home_config=home_config,
                           contact=contact_data,
                           services=services)

@main.route("/teklifal")
def getoffer():
    home_config = HomeConfig.query.first() or HomeConfig()

    contact_data = Contact.query.first()
    if not contact_data:
        contact_data = Contact()

    getoffer_data = Getoffer.query.first()
    if not getoffer_data:
        getoffer_data = Getoffer()

    services = Service.query.filter_by(is_active=True).order_by(Service.order.desc()).limit(6).all()

    return render_template('contact.html', # Teklif al için genellikle contact şablonu veya ayrı bir şablon kullanılır
                           home_config=home_config,
                           contact=contact_data,
                           getoffer=getoffer_data,
                           services=services)

# --- YENİ EKLENEN: ÜRÜN DETAY ROTASI ---
@main.route("/urun/<string:slug>")
def product_detail(slug):
    # 1. Genel ayarları çek (Header/Footer için gerekebilir)
    home_config = HomeConfig.query.first() or HomeConfig()
    
    # 2. Ürünü Slug ile bul, eğer yoksa veya pasifse 404 hatası ver
    product = Product.query.filter_by(slug=slug, is_active=True).first_or_404()
    
    # 3. Breadcrumb ve "Benzer Ürünler" için ana hizmeti belirle
    # Ürün birden fazla hizmete bağlı olabilir, ilkini ana kategori kabul ediyoruz.
    main_service = product.services[0] if product.services else None
    
    # 4. Menü/Footer için servis listesi (Standart yapı)
    services = Service.query.filter_by(is_active=True).order_by(Service.order.desc()).limit(6).all()

    return render_template('product_detail.html',
                           product=product,
                           main_service=main_service,
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
        data = request.form.to_dict()
        data.pop('form_id', None)
        data.pop('kvkk', None)
        data.pop('csrf_token', None)

        json_data = json.dumps(data, ensure_ascii=False)
        
        submission = FormSubmission(
            form_id=form_id,
            submission_data=json_data,
            ip_address=request.remote_addr
        )

        db.session.add(submission)
        db.session.commit()

        if form_obj.recipient_email:
            try:
                target_email = form_obj.recipient_email
                payload = data.copy()

                # FormSubmit Ayarları
                payload['_subject'] = f"Yeni Mesaj: {form_obj.title}"
                payload['_captcha'] = "false"
                payload['_template'] = "table"

                # Reply-to ayarı
                for key, value in data.items():
                    if 'mail' in key.lower() or 'e-posta' in key.lower():
                        payload['_replyto'] = value
                        break
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Referer': request.url
                }

                response = requests.post(
                    f"https://formsubmit.co/{target_email}", 
                    data=payload, 
                    headers=headers,
                    timeout=10
                )

                if response.status_code != 200:
                    current_app.logger.error(f"FormSubmit HATA KODU: {response.status_code}")
                    current_app.logger.error(f"FormSubmit HATA MESAJI: {response.text}")
                else:
                    current_app.logger.info(f"Mail başarıyla gönderildi: {target_email}")
                
            except Exception as mail_error:
                current_app.logger.error(f"FormSubmit bağlantı hatası (Form ID: {form_id}): {mail_error}")
        
        else:
            current_app.logger.warning(f"Form ID: {form_id} için 'recipient_email' tanımlı değil.")

        success_msg = form_obj.success_message or "Mesajınız başarıyla iletildi. Teşekkür ederiz."
        flash(success_msg, 'success')

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Form gönderim hatası: {e}")
        flash('Bir hata oluştu, lütfen tekrar deneyiniz.', 'danger')

    return redirect(request.referrer or url_for('main.contact'))