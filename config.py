import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'cok-gizli-bir-anahtar-buraya'

    uri = os.environ.get('DATABASE_URL')
    
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = uri or 'sqlite:///' + os.path.join(basedir, 'ekosan.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_PATH = os.environ.get('UPLOAD_PATH') or os.path.join(basedir, 'app/static/uploads')

    if not os.path.exists(UPLOAD_PATH):
        try:
            os.makedirs(UPLOAD_PATH)
        except OSError:
            pass