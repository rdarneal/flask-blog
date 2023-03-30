import os
import dotenv
basedir = os.path.abspath(os.path.dirname(__file__))
dotenv.load_dotenv(dotenv.find_dotenv())

class Config(object):
    # SECRET_KEY = secrets.token_urlsafe(64)
    SECRET_KEY = os.getenv('SECRET_KEY') or 'difficult-to-guess-string'
    POSTS_PER_PAGE = 3
    
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQL_ALCHEMY_TRACKMODIFICATIONS = False

    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT'))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS') is not None
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL') is not None
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    ADMINS = [''] # enter email 'your-email@example.com'
    ELASTICSEARCH_URL = os.getenv('ELASTICSEARCH_URL')