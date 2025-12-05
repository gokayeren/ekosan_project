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

db = SQLAlchemy()
migrate = Migrate()

admin = Admin(
    name='Ekosan Panel',
    index_view=AdminIndexView(name='Genel Bakış', url='/admin')
)
admin.base_template = 'admin/master.html'

from app.models import SiteSetting, MenuItem, HomeConfig, SliderGroup, SliderItem, Service, Footer

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
        'site_title',
        'logo_path',
        'favicon_path',
        'phone_number',
        'email_address',
        'address',
        'facebook_url',
        'instagram_url',
        'youtube_url'
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
        'description',
        'shop_address',
        'storage_address',
        'shop_tel',
        'mobile_tel',
        'email',
        'link01_text', 'link01_url',
        'link02_text', 'link02_url',
        'link03_text', 'link03_url',
        'link04_text', 'link04_url',
        'link05_text', 'link05_url',
        'policy_text', 'policy_url',
        'kvkk_text', 'kvkk_url',
        'cookies_text', 'cookies_url',
        'copyright'
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

    form_columns = (
        'parent',
        'label',
        'url',
        'action_text',
        'action_url',
        'order',
        'is_active',
    )

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
    if not os.path.exists(path):
        os.makedirs(path)

    form_extra_fields = {
        'hero_image': ImageUploadField('Hero Görseli', base_path=path, url_relative_path='uploads/'),
        'parallax_image': ImageUploadField('Parallax Görseli', base_path=path, url_relative_path='uploads/'),
        'cta_image': ImageUploadField('Uzman Resmi', base_path=path, url_relative_path='uploads/')
    }

    form_columns = (
        'hero_slider',
        'presentation_title',
        'presentation_subtitle',
        'presentation_action_text',
        'presentation_action_url',
        'features_title',
        'features_subtitle',
        'parallax_title',
        'parallax_subtitle',
        'parallax_image',
        'cta_title_bold',
        'cta_title_light',
        'cta_intro_text',
        'cta_btn_text',
        'cta_description',
        'cta_image',
        'slider_description',
        'slider_select'
    )

    @expose('/')
    def index_view(self):
        first_config = self.model.query.first()
        if first_config:
            url = url_for('.edit_view', id=first_config.id)
            return redirect(url)
        return super(HomeConfigView, self).index_view()
    
class SliderItemInline(InlineFormAdmin):
    form_columns = ('id', 'image_path', 'title', 'subtitle', 'btn_text', 'btn_link', 'order')
    form_label = 'Slayt Görseli'

    path = op.join(op.dirname(__file__), 'static', 'uploads')
    if not os.path.exists(path): os.makedirs(path)

    form_extra_fields = {
        'image_path': ImageUploadField('Resim Dosyası', base_path=path, url_relative_path='uploads/')
    }

class SliderGroupView(ModelView):
    create_template = 'admin/slider_form.html'
    edit_template = 'admin/slider_form.html'

    column_list = ('name', 'group_key', 'item_count')
    column_labels = {'name': 'Slider Adı', 'group_key': 'Anahtar (Key)', 'item_count': 'Görsel Sayısı'}

    form_columns = ('name', 'group_key')

    inline_models = (SliderItemInline(SliderItem),)

    def _item_count(view, context, model, name):
        return len(model.items)
    
    column_formatters = {
        'item_count': _item_count
    }

class ServiceView(ModelView):
    create_template = 'admin/service_form.html'
    edit_template = 'admin/service_form.html'

    column_list = ('title', 'order', 'is_active')
    column_default_sort = ('order', False)

    form_columns = (
        'title',
        'description',
        'image_path',
        'products',
        'order',
        'is_active'
    )

    path = op.join(op.dirname(__file__), 'static', 'uploads')
    if not os.path.exists(path):
        os.makedirs(path)

    form_extra_fields = {
        'image_path': ImageUploadField('Hizmet Görseli', base_path=path, url_relative_path='uploads/')
    }
    
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    admin.init_app(app)

    admin.add_view(SettingsView(SiteSetting, db.session, name="Genel Ayarlar"))
    admin.add_view(FooterView(Footer, db.session, name="Footer Ayarları")) # Footer Eklendi
    admin.add_view(MenuView(MenuItem, db.session, name="Navigasyon"))
    admin.add_view(HomeConfigView(HomeConfig, db.session, name="Anasayfa İçerik"))
    admin.add_view(SliderGroupView(SliderGroup, db.session, name="Slider Yönetimi", category="Medya"))
    admin.add_view(ServiceView(Service, db.session, name="Hizmetler", category="Ürün & Hizmet"))

    from app.main import main
    app.register_blueprint(main)

    @app.context_processor
    def inject_global_data():
        settings = SiteSetting.query.first()
        menu = MenuItem.query.filter_by(parent_id=None, is_active=True).order_by(MenuItem.order).all()
        footer = Footer.query.first()

        def get_slider(key):
            group = SliderGroup.query.filter_by(group_key=key).first()
            if group:
                return group.items
            return []

        return dict(
            site_settings=settings, 
            menu_items=menu, 
            footer_settings=footer, 
            get_slider=get_slider
        )

    return app