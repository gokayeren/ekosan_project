import os
import os.path as op
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.form.upload import ImageUploadField
from flask_admin.model.form import InlineFormAdmin
from config import Config
import json
from markupsafe import Markup

db = SQLAlchemy()
migrate = Migrate()

admin = Admin(
    name='Ekosan Panel',
    index_view=AdminIndexView(name='Genel Bakış', url='/admin')
)
admin.base_template = 'admin/master.html'

from app.models import (
    SiteSetting, MenuItem, HomeConfig, Corporate, References, 
    SliderGroup, SliderItem, Service, Footer, 
    Contact, Getoffer, Form, FormField, FormSubmission,
    FaqGroup, FaqItem
)

class SettingsView(ModelView):
    can_delete = False
    def can_create(self):
        return self.model.query.count() == 0

    edit_template = 'admin/header_settings.html' 
    create_template = 'admin/header_settings.html'

    path = op.join(op.dirname(__file__), 'static', 'uploads')
    if not os.path.exists(path):
        os.makedirs(path)

    form_extra_fields = {
        'logo_path': ImageUploadField('Site Logosu', base_path=path, url_relative_path='uploads/'),
        'favicon_path': ImageUploadField('Favicon', base_path=path, url_relative_path='uploads/')
    }

    form_columns = (
        'site_title', 'logo_path', 'favicon_path', 'phone_number',
        'email_address', 'address', 'facebook_url', 'instagram_url', 'youtube_url'
    )

    @expose('/')
    def index_view(self):
        first_setting = self.model.query.first()
        if first_setting:
            url = url_for('.edit_view', id=first_setting.id)
            return redirect(url)
        return super(SettingsView, self).index_view()

class FooterView(ModelView):
    can_delete = False
    def can_create(self):
        return self.model.query.count() == 0

    edit_template = 'admin/footer_settings.html' 
    create_template = 'admin/footer_settings.html'

    form_columns = (
        'description', 'shop_address', 'storage_address', 'shop_tel', 'mobile_tel', 'email',
        'link01_text', 'link01_url', 'link02_text', 'link02_url',
        'link03_text', 'link03_url', 'link04_text', 'link04_url', 'link05_text', 'link05_url',
        'policy_text', 'policy_url', 'kvkk_text', 'kvkk_url',
        'cookies_text', 'cookies_url', 'copyright'
    )

    column_labels = {
        'description': 'Footer Açıklama',
        'shop_address': 'Mağaza Adresi',
        'storage_address': 'Depo Adresi',
        'shop_tel': 'Sabit Tel',
        'mobile_tel': 'Cep Tel',
        'email': 'E-Posta',
        'copyright': 'Telif Hakkı Yazısı'
    }

    @expose('/')
    def index_view(self):
        first_footer = self.model.query.first()
        if first_footer:
            url = url_for('.edit_view', id=first_footer.id)
            return redirect(url)
        return super(FooterView, self).index_view()

class MenuView(ModelView):
    list_template = 'admin/menu_list.html'
    create_template = 'admin/menu_form.html'
    edit_template = 'admin/menu_form.html'

    column_list = ('order', 'label', 'url', 'parent', 'action_text', 'is_active')
    column_default_sort = ('order', False)

    form_columns = ('parent', 'label', 'url', 'action_text', 'action_url', 'order', 'is_active')
    batch_actions = None

    def is_action_allowed(self, name):
        return False

    def on_model_change(self, form, model, is_created):
        if not model.url:
            model.url = "#"
        return super(MenuView, self).on_model_change(form, model, is_created)

class HomeConfigView(ModelView):
    can_delete = False
    def can_create(self):
        return self.model.query.count() == 0

    edit_template = 'admin/home_config.html'
    create_template = 'admin/home_config.html'

    path = op.join(op.dirname(__file__), 'static', 'uploads')
    if not os.path.exists(path): os.makedirs(path)

    form_extra_fields = {
        'hero_image': ImageUploadField('Hero Görseli', base_path=path, url_relative_path='uploads/'),
        'parallax_image': ImageUploadField('Parallax Görseli', base_path=path, url_relative_path='uploads/'),
        'cta_image': ImageUploadField('Uzman Resmi', base_path=path, url_relative_path='uploads/')
    }

    form_columns = (
        'hero_slider', 'presentation_title', 'presentation_subtitle',
        'presentation_action_text', 'presentation_action_url',
        'features_title', 'features_subtitle',
        'parallax_title', 'parallax_subtitle', 'parallax_image',
        'cta_title_bold', 'cta_title_light', 'cta_intro_text',
        'cta_btn_text', 'cta_description', 'cta_image',
        'slider_description', 'slider_select'
    )

    @expose('/')
    def index_view(self):
        first_config = self.model.query.first()
        if first_config:
            url = url_for('.edit_view', id=first_config.id)
            return redirect(url)
        return super(HomeConfigView, self).index_view()

class CorporateView(ModelView):
    can_delete = False
    def can_create(self):
        return self.model.query.count() == 0

    edit_template = 'admin/corporate_config.html'
    create_template = 'admin/corporate_config.html'

    form_columns = (
        'hero_slider', 'presentation_slider', 'presentation_title',
        'howeare', 'whatwedo', 'whyus',
        'card01_title', 'card01_subtitle', 'card02_title', 'card02_subtitle',
        'card03_title', 'card03_subtitle', 'card04_title', 'card04_subtitle'
    )

    @expose('/')
    def index_view(self):
        first_config = self.model.query.first()
        if first_config:
            url = url_for('.edit_view', id=first_config.id)
            return redirect(url)
        return super(CorporateView, self).index_view()

class ReferencesView(ModelView):
    can_delete = False
    def can_create(self):
        return self.model.query.count() == 0

    edit_template = 'admin/references_config.html'
    create_template = 'admin/references_config.html'

    path = op.join(op.dirname(__file__), 'static', 'uploads')
    if not os.path.exists(path): os.makedirs(path)

    form_extra_fields = {
        'parallax_image': ImageUploadField('Parallax Görseli', base_path=path, url_relative_path='uploads/')
    }

    form_columns = ('hero_slider', 'presentation_title', 'corporate_slider', 'personal_slider', 'parallax_image', 'parallax_title')

    @expose('/')
    def index_view(self):
        first_config = self.model.query.first()
        if first_config:
            url = url_for('.edit_view', id=first_config.id)
            return redirect(url)
        return super(ReferencesView, self).index_view()

class ContactView(ModelView):
    can_delete = False
    def can_create(self):
        return self.model.query.count() == 0

    edit_template = 'admin/contact_config.html'
    create_template = 'admin/contact_config.html'

    form_columns = (
        'hero_slider', 'contact_form', 'contact_info_title',
        'shop_id', 'shop_id_date', 'tax_id', 'phone', 'wa', 'email',
        'workhours', 'location_shop', 'location_storage'
    )
    
    column_labels = {
        'hero_slider': 'Üst Slider Seçimi',
        'contact_form': 'İletişim Formu Seçimi',
        'contact_info_title': 'Firma Resmi Unvanı',
        'phone': 'Telefon', 'wa': 'WhatsApp', 'location_shop': 'Mağaza Adresi'
    }

    @expose('/')
    def index_view(self):
        first_config = self.model.query.first()
        if first_config:
            url = url_for('.edit_view', id=first_config.id)
            return redirect(url)
        return super(ContactView, self).index_view()

class GetofferView(ModelView):
    can_delete = False
    def can_create(self):
        return self.model.query.count() == 0

    edit_template = 'admin/getoffer_config.html'
    create_template = 'admin/getoffer_config.html'

    form_columns = ('hero_slider', 'getoffer_form', 'getoffer_title')
    column_labels = {'hero_slider': 'Üst Slider Seçimi', 'getoffer_form': 'İletişim Formu Seçimi', 'getoffer_title': 'Form başlığı'}

    @expose('/')
    def index_view(self):
        first_config = self.model.query.first()
        if first_config:
            url = url_for('.edit_view', id=first_config.id)
            return redirect(url)
        return super(GetofferView, self).index_view()

class FormFieldInline(InlineFormAdmin):
    form_label = 'Form Alanı'
    form_columns = ('id', 'label', 'name', 'field_type', 'is_required', 'placeholder', 'options', 'order')
    column_labels = {
        'label': 'Etiket', 'name': 'Sistem Adı', 'field_type': 'Tip', 
        'options': 'Seçenekler', 'is_required': 'Zorunlu'
    }

class FormBuilderView(ModelView):
    list_template = 'admin/form_list.html'
    create_template = 'admin/form_builder.html'
    edit_template = 'admin/form_builder.html'
    column_list = ('title', 'form_key', 'recipient_email')
    column_labels = {'title': 'Form Başlığı', 'form_key': 'Anahtar', 'recipient_email': 'Bildirim E-postası'}
    form_columns = ('title', 'form_key', 'recipient_email', 'submit_btn_text', 'success_message')
    inline_models = (FormFieldInline(FormField),)
    batch_actions = None
    def is_action_allowed(self, name): return False

class FormSubmissionView(ModelView):
    can_create = False
    can_edit = False
    can_delete = True
    list_template = 'admin/custom_list.html'
    column_list = ('form', 'created_at', 'submission_data', 'ip_address')
    column_default_sort = ('created_at', True)
    column_labels = {'form': 'Form Adı', 'created_at': 'Tarih', 'submission_data': 'Başvuru Detayları', 'ip_address': 'IP Adresi'}
    batch_actions = None
    def is_action_allowed(self, name): return False

    def _format_data(view, context, model, name):
        if not model.submission_data: return ""
        try:
            data_dict = json.loads(model.submission_data)
            html_content = '<ul style="list-style:none; padding:0; margin:0;">'
            for key, value in data_dict.items():
                readable_key = key.replace('_', ' ').capitalize()
                html_content += f'<li><strong>{readable_key}:</strong> {value}</li>'
            html_content += '</ul>'
            return Markup(html_content)
        except: return model.submission_data

    column_formatters = {'submission_data': _format_data}

class SliderItemInline(InlineFormAdmin):
    form_columns = ('id', 'image_path', 'title', 'subtitle', 'btn_text', 'btn_link', 'order')
    form_label = 'Slayt Görseli'
    path = op.join(op.dirname(__file__), 'static', 'uploads')
    if not os.path.exists(path): os.makedirs(path)
    form_extra_fields = {'image_path': ImageUploadField('Resim Dosyası', base_path=path, url_relative_path='uploads/')}

    batch_actions = None
    def is_action_allowed(self, name): 
        if name == 'delete': return True
        return False

class SliderGroupView(ModelView):
    list_template = 'admin/custom_list.html'
    create_template = 'admin/slider_form.html'
    edit_template = 'admin/slider_form.html'
    column_list = ('name', 'group_key', 'item_count')
    column_labels = {'name': 'Slider Adı', 'group_key': 'Anahtar', 'item_count': 'Görsel Sayısı'}
    form_columns = ('name', 'group_key')
    inline_models = (SliderItemInline(SliderItem),)
    def _item_count(view, context, model, name): return len(model.items)
    column_formatters = {'item_count': _item_count}

    batch_actions = None
    def is_action_allowed(self, name): 
        if name == 'delete': return True
        return False

class ServiceView(ModelView):
    list_template = 'admin/service_list.html'
    create_template = 'admin/service_form.html'
    edit_template = 'admin/service_form.html'

    column_list = ('image_path', 'title', 'slug', 'order', 'is_active')
    column_default_sort = ('order', False)

    form_columns = (
        'title',
        'subtitle',
        'slug',
        'slider_group',
        'faq_group',
        'features_title',
        'features',
        'video_btn_text',
        'video_url',
        'description_title',
        'description',
        'short_description',
        'image_path',
        'detail_image_path',
        'order',
        'is_active',
        'meta_title', 
        'meta_description', 
        'meta_keywords'
    )

    column_labels = {
        'title': 'Sayfa Başlığı',
        'subtitle': 'Üst Alt Başlık (Intro)',
        'slider_group': 'Soldaki Slider Seçimi',
        'faq_group': 'Sıkça Sorulan Sorular (SSS)',
        'features_title': 'Sağ Kısım Başlığı',
        'features': 'Sağ Kısım Özellikler (Liste)',
        'video_btn_text': 'Video Buton Yazısı',
        'video_url': 'Video Linki',
        'description_title': 'Alt Açıklama Başlığı',
        'description': 'Alt Detaylı Açıklama',
        'image_path': 'Liste Görseli',
        'detail_image_path': 'Header Kapak Görseli',
        'order': 'Sıralama',
        'is_active': 'Yayında mı?',
        'meta_title': 'SEO Başlığı',
        'meta_description': 'SEO Açıklaması',
        'meta_keywords': 'SEO Anahtar Kelimeler'
    }

    form_widget_args = {
        'features': {
            'rows': 10,
            'class': 'form-control' 
        },
        'description': {
            'rows': 10,
            'class': 'form-control'
        }
    }

    path = op.join(op.dirname(__file__), 'static', 'uploads')
    if not os.path.exists(path):
        os.makedirs(path)

    form_extra_fields = {
        'image_path': ImageUploadField('Liste Görseli', base_path=path, url_relative_path='uploads/'),
        'detail_image_path': ImageUploadField('Detay Sayfa Görseli', base_path=path, url_relative_path='uploads/')
    }

    batch_actions = None
    def is_action_allowed(self, name): 
        if name == 'delete': return True
        return False
    
class FaqItemInline(InlineFormAdmin):
    form_label = 'Soru & Cevap'
    form_columns = ('id', 'question', 'answer', 'order', 'is_active')
    form_widget_args = {
        'answer': {
            'rows': 4,
            'class': 'form-control'
        }
    }
    batch_actions = None
    def is_action_allowed(self, name): return False

class FaqGroupView(ModelView):
    list_template = 'admin/faq_list.html'
    create_template = 'admin/faq_form.html'
    edit_template = 'admin/faq_form.html'
    
    column_list = ('name', 'group_key', 'item_count')
    column_labels = {'name': 'SSS Grup Adı', 'group_key': 'Anahtar (Key)', 'item_count': 'Soru Sayısı'}
    
    form_columns = ('name', 'group_key', 'items')
    
    inline_models = (FaqItemInline(FaqItem),)
    
    def _item_count(view, context, model, name): return len(model.items)
    column_formatters = {'item_count': _item_count}
    
    batch_actions = None
    def is_action_allowed(self, name): 
        if name == 'delete': return True
        return False

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    admin.init_app(app)

    admin.add_view(SettingsView(SiteSetting, db.session, name="Genel Ayarlar"))
    admin.add_view(FooterView(Footer, db.session, name="Footer Ayarları"))
    admin.add_view(MenuView(MenuItem, db.session, name="Navigasyon"))
    admin.add_view(HomeConfigView(HomeConfig, db.session, name="Anasayfa İçerik"))
    admin.add_view(CorporateView(Corporate, db.session, name="Kurumsal İçerik"))
    admin.add_view(ReferencesView(References, db.session, name="Referanslar İçerik"))
    admin.add_view(ContactView(Contact, db.session, name="İletişim Sayfası"))
    admin.add_view(GetofferView(Getoffer, db.session, name="Teklif Sayfası"))
    admin.add_view(FormBuilderView(Form, db.session, name="Form Oluşturucu", category="Form Yönetimi"))
    admin.add_view(FormSubmissionView(FormSubmission, db.session, name="Gelen Başvurular", category="Form Yönetimi"))
    admin.add_view(SliderGroupView(SliderGroup, db.session, name="Slider Yönetimi", category="Sliderlar"))
    admin.add_view(FaqGroupView(FaqGroup, db.session, name="SSS Yönetimi", category="Sıkça Sorulan Sorular"))
    admin.add_view(ServiceView(Service, db.session, name="Hizmetler", category="Hizmet Yönetimi"))

    from app.main import main
    app.register_blueprint(main)

    @app.context_processor
    def inject_global_data():
        try:
            settings = SiteSetting.query.first()
            menu = MenuItem.query.filter_by(parent_id=None, is_active=True).order_by(MenuItem.order).all()
            footer = Footer.query.first()
        except:
            settings = None
            menu = []
            footer = None

        def get_slider(key):
            try:
                group = SliderGroup.query.filter_by(group_key=key).first()
                if group: return group.items
            except: pass
            return []
        
        from app.models import Form 
        def get_form(key):
            try:
                form_obj = Form.query.filter_by(form_key=key).first()
                return form_obj
            except: return None

        from app.models import FaqGroup
        def get_faq(key):
            """Verilen key'e sahip SSS grubunun sorularını döndürür."""
            try:
                group = FaqGroup.query.filter_by(group_key=key).first()
                if group: return group.items
            except: pass
            return []

        return dict(
            site_settings=settings, 
            menu_items=menu, 
            footer_settings=footer, 
            get_slider=get_slider,
            get_form=get_form,
            get_faq=get_faq
        )

    with app.app_context():
        from sqlalchemy.exc import OperationalError, ProgrammingError

        try:
            if not HomeConfig.query.first():
                print(">> Veritabanı boş: Varsayılan HomeConfig oluşturuluyor...")
                db.session.add(HomeConfig())
                db.session.commit()

            if not Corporate.query.first():
                db.session.add(Corporate())
                db.session.commit()

            if not References.query.first():
                db.session.add(References())
                db.session.commit()

            if not Contact.query.first():
                db.session.add(Contact())
                db.session.commit()

            if not Getoffer.query.first():
                db.session.add(Getoffer())
                db.session.commit()

            if not SiteSetting.query.first():
                db.session.add(SiteSetting(site_title="Ekosan Web Sitesi"))
                db.session.commit()

            if not Footer.query.first():
                 db.session.add(Footer())
                 db.session.commit()
                 
        except (OperationalError, ProgrammingError):
            print(">> UYARI: Tablolar henüz yok veya şema uyuşmazlığı var. 'flask db upgrade' bekleniyor...")
            db.session.rollback()
            pass

    return app