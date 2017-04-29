import os
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_sslify import SSLify
from flask_stormpath import StormpathManager


def set_config(app):
    """Set Flask app configuration
    """

    SSLify(app)
    Bootstrap(app)
    app.config.from_object(os.environ['APP_SETTINGS'])

    # Set up SQLAlchemy DB
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
    db = SQLAlchemy(app)

    # AWS credentials
    app.config['AWS_RDS_HOST'] = os.environ['AWS_RDS_HOST']
    app.config['AWS_RDS_USER'] = os.environ['AWS_RDS_USER']
    app.config['AWS_RDS_PASSWORD'] = os.environ['AWS_RDS_PASSWORD']
    app.config['AWS_ES_ACCESS_KEY'] = os.environ['AWS_ACCESS_KEY_ID']
    app.config['AWS_ES_SECRET_KEY'] = os.environ['AWS_SECRET_ACCESS_KEY']

    # OAuth credentials and configuration
    app.config['SECRET_KEY'] = os.environ['STORMPATH_SECRET_KEY']
    app.config['STORMPATH_API_KEY_ID'] = os.environ['STORMPATH_API_KEY_ID']
    app.config['STORMPATH_API_KEY_SECRET'] = os.environ[
        'STORMPATH_API_KEY_SECRET']
    app.config['STORMPATH_APPLICATION'] = os.environ['STORMPATH_APPLICATION']
    app.config['STORMPATH_ENABLE_MIDDLE_NAME'] = False
    app.config['STORMPATH_ENABLE_FORGOT_PASSWORD'] = True
    StormpathManager(app)

    return db
