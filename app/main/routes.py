from flask import render_template
from app.main import main
from app.models import HomeConfig, Corporate, References, Product, Service, SliderGroup

@main.route("/")
def index():
    home_config = HomeConfig.query.first()
    if not home_config:
        home_config = HomeConfig()

    services = Service.query.filter_by(is_active=True).order_by(Service.order.desc()).limit(6).all()

    return render_template('index.html',
                           home_config=home_config,
                           services=services)

@main.route("/corporate")
def corporate():
    home_config = HomeConfig.query.first()
    if not home_config:
        home_config = HomeConfig()

    corporate_data = Corporate.query.first()
    
    if not corporate_data:
        corporate_data = Corporate() 

    services = Service.query.filter_by(is_active=True).order_by(Service.order.desc()).limit(6).all()

    return render_template('corporate.html',
                           home_config=home_config,
                           corporate=corporate_data,
                           services=services)

@main.route("/references")
def references():
    home_config = HomeConfig.query.first()
    if not home_config:
        home_config = HomeConfig()

    references_data = References.query.first()
    
    if not references_data:
        references_data = References() 

    services = Service.query.filter_by(is_active=True).order_by(Service.order.desc()).limit(6).all()

    return render_template('references.html',
                           home_config=home_config,
                           references=references_data,
                           services=services)