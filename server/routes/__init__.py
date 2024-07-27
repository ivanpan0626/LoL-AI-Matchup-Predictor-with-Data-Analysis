from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    #app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
    #app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:123123123@localhost:5432/lol_website'
    CORS(app, supports_credentials=True)

    from routes.search import search
    from routes.views import views
    from routes.models import models
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(search, url_prefix='/')
    app.register_blueprint(models, url_prefix='/ai')

    return app