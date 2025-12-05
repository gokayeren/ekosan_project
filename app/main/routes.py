from flask import render_template
from app.main import main
from app.models import HomeConfig, Product, Service, SliderGroup

@main.route("/")
def index():
    home_config = HomeConfig.query.first()
    if not home_config:
        home_config = HomeConfig()

    services = Service.query.filter_by(is_active=True).order_by(Service.order.desc()).limit(6).all()

    return render_template('index.html',
                           home_config=home_config,
                           services=services)

@main.route("/iletisim")
def contact():
    return render_template('index.html')