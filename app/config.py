from os import path, environ
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_sslify import SSLify
from flask_stormpath import StormpathManager


def set_config(app):
    """Set Flask app configuration
    """

    SSLify(app)
    Bootstrap(app)
    app.config.from_object(environ['APP_SETTINGS'])

    # Set up SQLAlchemy DB
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = environ['DATABASE_URL']
    db = SQLAlchemy(app)

    # RDS credentials
    app.config['RDS_HOST'] = environ['RDS_HOST']
    app.config['RDS_USER'] = environ['RDS_USER']
    app.config['RDS_PASSWORD'] = environ['RDS_PASSWORD']

    # OAuth credentials and configuration
    app.config['SECRET_KEY'] = environ['STORMPATH_SECRET_KEY']
    app.config['STORMPATH_API_KEY_ID'] = environ['STORMPATH_API_KEY_ID']
    app.config['STORMPATH_API_KEY_SECRET'] = environ[
        'STORMPATH_API_KEY_SECRET']
    app.config['STORMPATH_APPLICATION'] = environ['STORMPATH_APPLICATION']
    app.config['STORMPATH_ENABLE_MIDDLE_NAME'] = False
    app.config['STORMPATH_ENABLE_FORGOT_PASSWORD'] = True
    StormpathManager(app)

    return db

path_app = path.dirname(path.abspath(__file__))
path_base = path.dirname(path_app)
path_models = path.join(path_base, 'models')
modelzip_bucket = 'comparatory'
modelzip_filename = 'models.zip'
AWS_SECRET_ACCESS_KEY = environ['AWS_SECRET_ACCESS_KEY']
AWS_ACCESS_KEY_ID = environ['AWS_ACCESS_KEY_ID']
