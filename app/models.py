from app import db
from datetime import datetime
from slugify import slugify

class SEOMixin:
    meta_title = db.Column(db.String(150))
    meta_description = db.Column(db.String(300))
    meta_keywords = db.Column(db.String(200))

    def set_seo(self, title, desc, keywords):
        self.meta_title = title
        self.meta_description = desc
        self.meta_keywords = keywords

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
    description = db.Column(db.Text, default="Biz, yenilikçi ve sürdürülebilir güneş enerjisi çözümleri sunan bir firmayız. Güneş enerjisi sistemlerinden ve solar kamera çözümlerine kadar geniş bir yelpazede teknolojiler sunarak, müşterilerimizin enerji verimliliği sağlayan çevre dostu çözümlerle tanışmasını sağlıyoruz.")
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
    shop_address = db.Column(db.String(200), default="Müftü Mah. Erdemir Cad. İstanbul Yol Ayrımı 118/C Kdz. Ereğli / ZONGULDAK")
    storage_address = db.Column(db.String(200), default="Soğanlıyörük Köyü, Delihakkı Mevkii, Güçbir Jeneratör Fabrikası Yanı Kdz. Ereğli / ZONGULDAK")
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
    
class HomeConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hero_slider = db.Column(db.String(50), nullable=True)
    presentation_title = db.Column(db.String(200), default="Sektöründe Kendini İspatlamış En Verimli Enerji Çözümleri Ekosan Isı' da.")
    presentation_subtitle = db.Column(db.Text, default="Ekosan Isı Olarak 20 Yıldır Bölgemize Hizmet Vermekten Onur Duyuyoruz.")
    presentation_action_text = db.Column(db.String(50), nullable=True)
    presentation_action_url = db.Column(db.String(200), nullable=True)
    features_title = db.Column(db.String(200), default="Mühendislik ve Güvenin Buluşması.")
    features_subtitle = db.Column(db.Text, default="Sadece bir ısıtma sistemi değil; yaşam kalitenizi artıran teknolojiler üretiyoruz.")
    parallax_title = db.Column(db.String(200), default="Gelecek nesiller için yaşam alanları tasarlıyoruz.")
    parallax_subtitle = db.Column(db.Text, default="1917 yılında bir ısıtma teknolojisi üreticisi olarak kurulan ve artık Carrier'ın bir parçası olarak verimli ısıtma, soğutma ve yenilenebilir enerji çözümleri alanında dünyanın önde gelen sağlayıcılarından biriyiz. Yerel partnerlerimizle birlikte, Gelecek nesiller için yaşam alanları tasarlamak her gün üstlendiğimiz bir sorumluluktur.")
    parallax_image = db.Column(db.String(200), default='default_parallax.png')
    cta_title_bold = db.Column(db.String(100), default="NASIL")
    cta_title_light = db.Column(db.String(200), default="YARDIMCI OLABİLİRİZ?")
    cta_intro_text = db.Column(db.Text, default="Ekosan Isı olarak ısıtma, soğutma, akıllı ve ekolojik ev konularında bölgemizde 20 yıldır faaliyet gösteriyoruz.")
    cta_btn_text = db.Column(db.String(200), default="Ücretsiz Keşif")
    cta_description = db.Column(db.Text, default="Yenilikçi ve verimli enerji çözümlerimiz için ücretsiz keşif ve fiyat talebinizi bırakabilirsiniz.")
    cta_image = db.Column(db.String(200), default='default_expert.png')
    slider_description = db.Column(db.Text, default="Isıtma, Soğutma ve Akıllı ev teknolojilerinde sektörün en iyileri ile birlikte çalışıyoruz.")
    slider_select = db.Column(db.String(50), nullable=True)

    def __str__(self):
        return "Anasayfa Sabit Ayarları"
    
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

    products = db.relationship('Product', secondary=products_services, lazy='subquery',
        backref=db.backref('services', lazy=True))

    def __repr__(self):
        return self.title
    
class SliderGroup(db.Model):
    __tablename__ = 'slider_groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    group_key = db.Column(db.String(50), unique=True, nullable=False)
    items = db.relationship('SliderItem', backref='group', lazy=True, cascade="all, delete-orphan", order_by="SliderItem.order")

    def __str__(self):
        return self.name

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

class Corporate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hero_slider = db.Column(db.String(50), nullable=True)
    presentation_slider = db.Column(db.String(50), nullable=True)
    presentation_title = db.Column(db.String(200), default="20 Yıldan Fazla Süredir Bölgemizde Hizmet Veriyoruz.")
    howeare = db.Column(db.Text, default="Ekosan Isı 20 yılı aşkın sektör deneyimiyle Zonguldak, Ereğli, Alaplı ve Akçakoca bölgelerinde kombi, klima, ısı pompası ve güneş enerjisinden elektrik üretimi (GES) alanlarında profesyonel çözümler sunan öncü bir firmadır.")
    whatwedo = db.Column(db.Text, default="Bölgenin en güvenilir ısıtma soğutma firmlarından biri olarak, enerji verimliliğini artıran modern sistemleri uzman kadromuzla kuruyor, bakımını yapıyor ve uzun yıllar sorunsuz çalışmasını sağlıyoruz.")
    whyus = db.Column(db.Text, default="2*+ yıllık uzmanlık. Bölgenin deneyimli Isıtma Soğutma Firması. Binlerce başarılı kurulum. Hızlı servis ve yerinde çözüm. Enerji tasarrufu odaklı mühendislik.")
    card01_title = db.Column(db.String(200), default="Isı Pompası Sistemleri")
    card01_subtitle = db.Column(db.Text, default="Enerji verimli ısı pompası projelendirme Alaplı ve Akçakoca ısı pompası kurulum. En verimli ısı pompası modelleri.")
    card02_title = db.Column(db.String(200), default="Kombi Sistemleri")
    card02_subtitle = db.Column(db.Text, default="Kombi montaj, bakım ve arıza tespiti. Zonguldak kombi servisi çözümleri. Uygun fiyatlı kombi bakım hizmetleri.")
    card03_title = db.Column(db.String(200), default="Klima Çözümleri")
    card03_subtitle = db.Column(db.Text, default="Profesyonel klima montajı. Ereğli klima servisi. Klima gaz dolumu ve periyodik bakım.")
    card04_title = db.Column(db.String(200), default="Güneş Enerjisinden Elektrik")
    card04_subtitle = db.Column(db.Text, default="Güneş paneli kurulumu. Akçakoca GES porjelendirme. Güneşten elektrik üretimi maliyet analizi.")

    def __str__(self):
        return "Kurumsal Sabit Ayarları"

class Product(db.Model, SEOMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(150), unique=True)
    price = db.Column(db.Float, nullable=True)
    description = db.Column(db.Text, nullable=False)
    tech_specs = db.Column(db.Text)
    image_file = db.Column(db.String(100), nullable=False, default='default.jpg')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def save(self):
        if not self.slug:
            self.slug = slugify(self.name)
        db.session.add(self)
        db.session.commit()