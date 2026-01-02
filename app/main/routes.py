import requests
import json
from flask import render_template, request, redirect, url_for, flash, current_app, abort
from app import db
from app.main import main
from app.models import (
    HomeConfig, Corporate, References, Contact, Getoffer,
    Service, Form, FormSubmission
)

def get_shared_data():
    home_config = HomeConfig.query.first() or HomeConfig()
    services = Service.query.filter_by(is_active=True).order_by(Service.order.asc()).all()
    return home_config, services

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

    return render_template('service_detail.html',
                           service=service,
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

                payload['_subject'] = f"Yeni Mesaj: {form_obj.title} - {request.host}"
                payload['_captcha'] = "false"
                payload['_template'] = "table"

                for key, value in data.items():
                    if 'mail' in key.lower() or 'e-posta' in key.lower():
                        payload['_replyto'] = value
                        break
                
                headers = {
                    'User-Agent': 'Ekosan-Flask-App',
                    'Referer': request.url
                }

                response = requests.post(
                    f"https://formsubmit.co/{target_email}", 
                    data=payload, 
                    headers=headers,
                    timeout=10
                )

                if response.status_code == 200:
                    current_app.logger.info(f"Mail başarıyla gönderildi: {target_email}")
                else:
                    current_app.logger.error(f"Mail gönderme hatası: {response.text}")
                
            except Exception as mail_error:
                current_app.logger.error(f"Mail sunucusu hatası: {mail_error}")
        
        success_msg = form_obj.success_message or "Mesajınız başarıyla iletildi."
        flash(success_msg, 'success')

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Form işlem hatası: {e}")
        flash('Bir hata oluştu, lütfen tekrar deneyiniz.', 'danger')

    return redirect(request.referrer or url_for('main.contact'))