from app import db
from datetime import datetime
from slugify import slugify

# --- 1. YARDIMCI SINIFLAR (MIXINS) ---
class SEOMixin:
    """
    Tüm sayfalara, ürünlere ve hizmetlere SEO özellikleri kazandırır.
    """
    meta_title = db.Column(db.String(150))
    meta_description = db.Column(db.String(300))
    meta_keywords = db.Column(db.String(200))

    def set_seo(self, title, desc, keywords):
        self.meta_title = title
        self.meta_description = desc
        self.meta_keywords = keywords

# --- 2. GENEL AYARLAR VE YAPILANDIRMA MODELLERİ (MEVCUT YAPI KORUNDU) ---

class SiteSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site_title = db.Column(db.String(100), default="Ekosan Isı")
    phone_number = db.Column(db.String(20), default="03723124838")
    email_address = db.Column(db.String(100), default="bilgi@ekosanmuhendislik.com")
    address = db.Column(db.Text, default="Müftü Mah. Erdemir Cad. İstanbul Yol Ayrımı 118/C Kdz.Ereğli / Zonguldak")
    logo_path = db.Column(db.String(200), default='logo.png')
    favicon_path = db.Column(db.String(200), default='favicon.png')
    facebook_url = db.Column(db.String(255), default='https://www.facebook.com/ekosanisi/')
    instagram_url = db.Column(db.String(255), default='https://www.instagram.com/ekosan_isi/')
    youtube_url = db.Column(db.String(255), default='https://www.youtube.com/@ekosanis4077')
    
    def __str__(self):
        return "Genel Site Ayarları"
    
class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(200), default="#")
    order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'), nullable=True)
    children = db.relationship('MenuItem', 
                               backref=db.backref('parent', remote_side=[id]),
                               lazy=True) 

    action_text = db.Column(db.String(50), nullable=True)
    action_url = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        if self.parent:
            return f"{self.parent.label} > {self.label}"
        return self.label
    
class Footer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, default="Biz, yenilikçi ve sürdürülebilir güneş enerjisi çözümleri sunan bir firmayız.")
    link01_text = db.Column(db.String(50), default="Isı Pompası")
    link01_url = db.Column(db.String(200), nullable=True)
    link02_text = db.Column(db.String(50), default="Ekolojik Villa")
    link02_url = db.Column(db.String(200), nullable=True)
    link03_text = db.Column(db.String(50), default="Güneşten Elektrik")
    link03_url = db.Column(db.String(200), nullable=True)
    link04_text = db.Column(db.String(50), default="Akıllı Ev")
    link04_url = db.Column(db.String(200), nullable=True)
    link05_text = db.Column(db.String(50), default="Keşif Formu")
    link05_url = db.Column(db.String(200), nullable=True)
    shop_address = db.Column(db.Text, default="Müftü Mah. Erdemir Cad. İstanbul Yol Ayrımı 118/C Kdz. Ereğli / ZONGULDAK")
    storage_address = db.Column(db.Text, default="Soğanlıyörük Köyü, Delihakkı Mevkii, Güçbir Jeneratör Fabrikası Yanı Kdz. Ereğli / ZONGULDAK")
    shop_tel = db.Column(db.String(50), default="03723124838")
    mobile_tel = db.Column(db.String(50), default="905334885033")
    email = db.Column(db.String(50), default="bilgi@ekosanmuhendislik.com")
    policy_text = db.Column(db.String(50), default="Gizlilik Politikası")
    policy_url = db.Column(db.String(200), nullable=True)
    kvkk_text = db.Column(db.String(50), default="KVKK Metni")
    kvkk_url = db.Column(db.String(200), nullable=True)
    cookies_text = db.Column(db.String(50), default="Çerezler")
    cookies_url = db.Column(db.String(200), nullable=True)
    copyright = db.Column(db.String(200), default="Copyright | Ekosan Isıtma ve Soğutma Sistemleri Mühendislik Ltd. Şti.")

    def __str__(self):
        return "Footer Sabit Ayarları"

class SliderGroup(db.Model):
    __tablename__ = 'slider_groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    group_key = db.Column(db.String(50), unique=True, nullable=False)
    items = db.relationship('SliderItem', backref='group', lazy=True, cascade="all, delete-orphan", order_by="SliderItem.order")

    def __str__(self):
        return f"{self.name} ({self.group_key})"

class SliderItem(db.Model):
    __tablename__ = 'slider_items'
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('slider_groups.id'), nullable=False)
    image_path = db.Column(db.String(255))
    title = db.Column(db.String(200))
    subtitle = db.Column(db.String(200))
    btn_text = db.Column(db.String(50))
    btn_link = db.Column(db.String(200))
    order = db.Column(db.Integer, default=0)

    def __str__(self):
        return self.title or "Slider Item"

class Form(db.Model):
    __tablename__ = 'forms'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    form_key = db.Column(db.String(50), unique=True, nullable=False)
    recipient_email = db.Column(db.String(150), nullable=True)
    submit_btn_text = db.Column(db.String(50), default="Gönder")
    success_message = db.Column(db.Text, default="Formunuz başarıyla iletildi. Teşekkür ederiz.")
    fields = db.relationship('FormField', backref='form', lazy=True, cascade="all, delete-orphan", order_by="FormField.order")

    def __str__(self):
        return f"{self.title} ({self.form_key})"

class FormField(db.Model):
    __tablename__ = 'form_fields'
    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.Integer, db.ForeignKey('forms.id'), nullable=False)
    label = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    field_type = db.Column(db.String(20), default='text')
    placeholder = db.Column(db.String(100), nullable=True)
    is_required = db.Column(db.Boolean, default=True)
    options = db.Column(db.Text, nullable=True)
    order = db.Column(db.Integer, default=0)

    def __str__(self):
        return self.label

class FormSubmission(db.Model):
    __tablename__ = 'form_submissions'
    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.Integer, db.ForeignKey('forms.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    submission_data = db.Column(db.Text, nullable=False) 
    ip_address = db.Column(db.String(50), nullable=True)
    form = db.relationship('Form')

    def __str__(self):
        return f"{self.form.title} - {self.created_at.strftime('%d.%m.%Y')}"

# --- SAYFA AYARLARI MODELLERİ (MEVCUT YAPI KORUNDU) ---

class HomeConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    hero_slider_id = db.Column(db.Integer, db.ForeignKey('slider_groups.id'), nullable=True)
    hero_slider = db.relationship('SliderGroup', foreign_keys=[hero_slider_id])
    
    presentation_title = db.Column(db.String(200), default="Sektöründe Kendini İspatlamış En Verimli Enerji Çözümleri Ekosan Isı' da.")
    presentation_subtitle = db.Column(db.Text, default="Ekosan Isı Olarak 20 Yıldır Bölgemize Hizmet Vermekten Onur Duyuyoruz.")
    presentation_action_text = db.Column(db.String(50), nullable=True)
    presentation_action_url = db.Column(db.String(200), nullable=True)
    features_title = db.Column(db.String(200), default="Mühendislik ve Güvenin Buluşması.")
    features_subtitle = db.Column(db.Text, default="Sadece bir ısıtma sistemi değil; yaşam kalitenizi artıran teknolojiler üretiyoruz.")
    parallax_title = db.Column(db.String(200), default="Gelecek nesiller için yaşam alanları tasarlıyoruz.")
    parallax_subtitle = db.Column(db.Text, default="1917 yılında bir ısıtma teknolojisi üreticisi olarak kurulan ve artık Carrier'ın bir parçası.")
    parallax_image = db.Column(db.String(200), default='default_parallax.png')
    cta_title_bold = db.Column(db.String(100), default="NASIL")
    cta_title_light = db.Column(db.String(200), default="YARDIMCI OLABİLİRİZ?")
    cta_intro_text = db.Column(db.Text, default="Ekosan Isı olarak ısıtma, soğutma, akıllı ve ekolojik ev konularında bölgemizde 20 yıldır faaliyet gösteriyoruz.")
    cta_btn_text = db.Column(db.String(200), default="Ücretsiz Keşif")
    cta_description = db.Column(db.Text, default="Yenilikçi ve verimli enerji çözümlerimiz için ücretsiz keşif ve fiyat talebinizi bırakabilirsiniz.")
    cta_image = db.Column(db.String(200), default='default_expert.png')
    slider_description = db.Column(db.Text, default="Isıtma, Soğutma ve Akıllı ev teknolojilerinde sektörün en iyileri ile birlikte çalışıyoruz.")
    
    slider_select_id = db.Column(db.Integer, db.ForeignKey('slider_groups.id'), nullable=True)
    slider_select = db.relationship('SliderGroup', foreign_keys=[slider_select_id])

    def __str__(self):
        return "Anasayfa Sabit Ayarları"
    
class Corporate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    hero_slider_id = db.Column(db.Integer, db.ForeignKey('slider_groups.id'), nullable=True)
    hero_slider = db.relationship('SliderGroup', foreign_keys=[hero_slider_id])

    presentation_slider_id = db.Column(db.Integer, db.ForeignKey('slider_groups.id'), nullable=True)
    presentation_slider = db.relationship('SliderGroup', foreign_keys=[presentation_slider_id])
    
    presentation_title = db.Column(db.String(200), default="20 Yıldan Fazla Süredir Bölgemizde Hizmet Veriyoruz.")
    howeare = db.Column(db.Text, default="Ekosan Isı 20 yılı aşkın sektör deneyimiyle Zonguldak...")
    whatwedo = db.Column(db.Text, default="Bölgenin en güvenilir ısıtma soğutma firmlarından biri olarak...")
    whyus = db.Column(db.Text, default="20+ yıllık uzmanlık...")
    card01_title = db.Column(db.String(200), default="Isı Pompası Sistemleri")
    card01_subtitle = db.Column(db.Text, default="Enerji verimli ısı pompası projelendirme...")
    card02_title = db.Column(db.String(200), default="Kombi Sistemleri")
    card02_subtitle = db.Column(db.Text, default="Kombi montaj, bakım ve arıza tespiti...")
    card03_title = db.Column(db.String(200), default="Klima Çözümleri")
    card03_subtitle = db.Column(db.Text, default="Profesyonel klima montajı...")
    card04_title = db.Column(db.String(200), default="Güneş Enerjisinden Elektrik")
    card04_subtitle = db.Column(db.Text, default="Güneş paneli kurulumu...")

    def __str__(self):
        return "Kurumsal Sabit Ayarları"
    
class References(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    hero_slider_id = db.Column(db.Integer, db.ForeignKey('slider_groups.id'), nullable=True)
    hero_slider = db.relationship('SliderGroup', foreign_keys=[hero_slider_id])
    
    presentation_title = db.Column(db.String(200), default="Isıtma, Soğutma, Güneşten Elektrik...")
    
    corporate_slider_id = db.Column(db.Integer, db.ForeignKey('slider_groups.id'), nullable=True)
    corporate_slider = db.relationship('SliderGroup', foreign_keys=[corporate_slider_id])
    
    personal_slider_id = db.Column(db.Integer, db.ForeignKey('slider_groups.id'), nullable=True)
    personal_slider = db.relationship('SliderGroup', foreign_keys=[personal_slider_id])
    
    parallax_image = db.Column(db.String(200), default='default_parallax.png')
    parallax_title = db.Column(db.Text, default="Binlerce Mutlu Müşterimiz Arasına Katılmak için...")

    def __str__(self):
        return "Referanslarımız Sabit Ayarları"
    
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    hero_slider_id = db.Column(db.Integer, db.ForeignKey('slider_groups.id'), nullable=True)
    hero_slider = db.relationship('SliderGroup', foreign_keys=[hero_slider_id])
    
    contact_form_id = db.Column(db.Integer, db.ForeignKey('forms.id'), nullable=True)
    contact_form = db.relationship('Form', foreign_keys=[contact_form_id])
    
    contact_info_title = db.Column(db.String(200), default="Ekosan Isıtma ve Soğutma...")
    shop_id = db.Column(db.String(200), default="5393")
    shop_id_date = db.Column(db.String(200), default="03.05.2005")
    tax_id = db.Column(db.String(200), default="336 238 12 86 ( E-Fatura )")
    phone = db.Column(db.String(200), default="0(372) 312 48 38")
    wa = db.Column(db.String(200), default="0 533 207 54 66")
    email = db.Column(db.String(200), default="bilgi@ekosanmuhendislik.com")
    workhours = db.Column(db.String(200), default="Pazartesi - Cumartesi 09:00 - 19:00")
    location_shop = db.Column(db.String(200), default="Müftü Mag. Erdemir Cad...")
    location_storage = db.Column(db.String(200), default="Soğanlıyörük Köyü Güçbir...")

    def __str__(self):
        return "İletişim Sabit Ayarları"
    
class Getoffer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    hero_slider_id = db.Column(db.Integer, db.ForeignKey('slider_groups.id'), nullable=True)
    hero_slider = db.relationship('SliderGroup', foreign_keys=[hero_slider_id])
    
    getoffer_form_id = db.Column(db.Integer, db.ForeignKey('forms.id'), nullable=True)
    getoffer_form = db.relationship('Form', foreign_keys=[getoffer_form_id])
    
    getoffer_title = db.Column(db.String(200), default="Ürün yada hizmetlerimiz hakkında bilgi almak...")

    def __str__(self):
        return "Teklif Al Sabit Ayarları"

# --- 3. ÜRÜN VE HİZMET İLİŞKİSİ VE MODELLERİ (GÜNCELLENEN KISIM) ---

# Çoktan çoğa ilişki tablosu (Ürünler <-> Hizmetler)
products_services = db.Table('products_services',
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True),
    db.Column('service_id', db.Integer, db.ForeignKey('service.id'), primary_key=True)
)
    
class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    image_path = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    order = db.Column(db.Integer, default=0)

    # Bir hizmetin içindeki ürünlere erişmek için
    products = db.relationship('Product', secondary=products_services, lazy='subquery',
        backref=db.backref('services', lazy=True))

    def __repr__(self):
        return self.title

class Product(db.Model, SEOMixin):
    """
    Gelişmiş Ürün Modeli:
    - SEO uyumlu (SEOMixin kullanır)
    - Zengin içerik (HTML açıklama)
    - E-ticaret özellikleri kaldırıldı (Satın al butonu yok)
    - Çoklu görsel desteği (ProductImage ilişkisi)
    """
    __tablename__ = 'product'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(150), unique=True)
    
    # Katalog Görünümü İçin Fiyat (Opsiyonel, sadece bilgi amaçlı)
    price = db.Column(db.Float, nullable=True)
    
    # İçerik Alanları
    short_description = db.Column(db.String(500), nullable=True) # Kartlarda gözükecek kısa özet
    description = db.Column(db.Text, nullable=False) # Detaylı uzun açıklama (HTML destekli)
    tech_specs = db.Column(db.Text, nullable=True) # Teknik Özellikler Tablosu (HTML veya JSON)
    
    # Ana Liste Görseli (Thumbnail)
    image_file = db.Column(db.String(100), nullable=False, default='default.jpg')
    
    # Durum Bilgileri
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # İLİŞKİ: Sınırsız Ekstra Görsel (Option 1, Option 2 gibi)
    images = db.relationship('ProductImage', backref='product', lazy=True, cascade="all, delete-orphan", order_by="ProductImage.order")

    def save(self):
        if not self.slug:
            self.slug = slugify(self.name)
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return self.name

class ProductImage(db.Model):
    """
    Ürünler için ekstra galeri resimleri veya seçenek resimleri.
    Örnek: 'İç Ünite Görünümü', 'Dış Ünite Görünümü' vb.
    """
    __tablename__ = 'product_images'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    image_path = db.Column(db.String(200), nullable=False)
    title = db.Column(db.String(100), nullable=True) # Resim başlığı (Örn: "Dış Cephe Görünümü")
    description = db.Column(db.String(255), nullable=True) # Resim altı kısa açıklama
    order = db.Column(db.Integer, default=0) # Sıralama

    def __repr__(self):
        return f"{self.title or 'Image'} ({self.product.name})"