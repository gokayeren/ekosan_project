import unittest

from app import create_app, db
from app.models import Service, SiteSetting, SliderGroup, SliderItem


class TestConfig:
    TESTING = True
    SECRET_KEY = 'test-secret'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False


class ServicePageRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app(TestConfig)
        cls.client = cls.app.test_client()

        with cls.app.app_context():
            db.create_all()
            products = SliderGroup(name='Ürünler', group_key='test-products')
            references = SliderGroup(name='Referanslar', group_key='test-references')
            db.session.add_all([products, references])
            db.session.flush()

            db.session.add_all([
                SliderItem(group_id=products.id, image_path='legacy.jpg', title=None),
                SliderItem(group_id=products.id, image_path='product.jpg', title='Test Ürünü'),
                SliderItem(
                    group_id=references.id,
                    image_path='reference.jpg',
                    title='Test Referansı',
                    video_url='https://youtu.be/dQw4w9WgXcQ'
                )
            ])
            db.session.add(Service(
                title='Akıllı Ev',
                slug='akilli-ev',
                slider_group_2_id=products.id,
                slider_group_3_id=references.id,
                is_active=True
            ))
            db.session.add(SiteSetting(product_detail_enabled=False))
            db.session.commit()

    @classmethod
    def tearDownClass(cls):
        with cls.app.app_context():
            db.drop_all()

    def test_service_page_handles_legacy_item_without_title(self):
        response = self.client.get('/hizmetler/akilli-ev')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Akıllı Ev Ürünü'.encode(), response.data)
        self.assertNotIn('Ürünü İncele'.encode(), response.data)

    def test_reference_youtube_opens_with_privacy_enhanced_embed(self):
        response = self.client.get('/hizmetler/akilli-ev')
        self.assertIn(b'youtube-nocookie.com/embed/dQw4w9WgXcQ', response.data)
        self.assertIn(b'reference-video-modal', response.data)

    def test_product_page_has_product_and_breadcrumb_schema(self):
        with self.app.app_context():
            item = SliderItem.query.filter_by(title='Test Ürünü').one()
            item_id = item.id
            settings = SiteSetting.query.first()
            settings.product_detail_enabled = True
            db.session.commit()

        response = self.client.get(f'/urunler/{item_id}/test-urunu')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'BreadcrumbList', response.data)
        self.assertIn(b'Product', response.data)

        with self.app.app_context():
            settings = SiteSetting.query.first()
            settings.product_detail_enabled = False
            db.session.commit()

    def test_product_page_is_404_while_feature_is_disabled(self):
        with self.app.app_context():
            item = SliderItem.query.filter_by(title='Test Ürünü').one()
            item_id = item.id

        response = self.client.get(f'/urunler/{item_id}/test-urunu')
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
