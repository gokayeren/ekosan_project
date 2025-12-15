import requests
import json
from flask import render_template, request, redirect, url_for, flash, current_app
from app import db
from app.main import main
from app.models import (
    HomeConfig, Corporate, References, Contact, Getoffer,
    Service, Form, FormSubmission
)

@main.route("/")
def index():
    home_config = HomeConfig.query.first()
    if not home_config:
        home_config = HomeConfig()

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

    return render_template('contact.html',
                           home_config=home_config,
                           contact=contact_data,
                           getoffer=getoffer_data,
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
                payload['_captcha'] = "false"  # Robot doğrulaması kapalı
                payload['_template'] = "table" # Görünüm tipi

                # Reply-to (Yanıtla) ayarı
                for key, value in data.items():
                    if 'mail' in key.lower() or 'e-posta' in key.lower():
                        payload['_replyto'] = value
                        break
                
                # --- KRİTİK DÜZELTME: HEADERS EKLENDİ ---
                # FormSubmit'in bizi "Python Script" değil "Tarayıcı" sanması için:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Referer': request.url  # İsteğin geldiği sayfa adresi
                }

                # İsteği gönderiyoruz ve yanıtı yakalıyoruz (response)
                response = requests.post(
                    f"https://formsubmit.co/{target_email}", 
                    data=payload, 
                    headers=headers, # Header'ı buraya ekledik
                    timeout=10 # Süreyi biraz uzattık
                )

                # --- HATA KONTROLÜ ---
                # Eğer işlem başarılı değilse (200 OK dönmediyse) hatayı loglayalım
                if response.status_code != 200:
                    current_app.logger.error(f"FormSubmit HATA KODU: {response.status_code}")
                    current_app.logger.error(f"FormSubmit HATA MESAJI: {response.text}")
                else:
                    current_app.logger.info(f"Mail başarıyla gönderildi: {target_email}")
                
            except Exception as mail_error:
                # Burası Python tarafındaki hataları yakalar (İnternet yok, DNS hatası vb.)
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