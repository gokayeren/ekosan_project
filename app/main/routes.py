import requests
import json
import os
import smtplib
from email.message import EmailMessage
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
            ip_address=request.remote_addr
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
                current_app.logger.error(f"Mail sunucusu hatası: {mail_error}")
        
        success_msg = form_obj.success_message or "Mesajınız başarıyla iletildi."
        flash(success_msg, 'success')

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Form işlem hatası: {e}")
        flash('Bir hata oluştu, lütfen tekrar deneyiniz.', 'danger')

    return redirect(request.referrer or url_for('main.contact'))