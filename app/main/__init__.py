from flask import Blueprint

# Blueprint'i burada 'main' adıyla tanımlıyoruz
main = Blueprint('main', __name__)

# Döngüsel import hatasını önlemek için route'ları en sonda çağırıyoruz
from . import routes