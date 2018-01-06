from os import path, environ
from flask_bootstrap import Bootstrap
from flask_sslify import SSLify


def set_config(app):
    """Set Flask app configuration
    """

    SSLify(app)
    Bootstrap(app)
    app.config.from_object(environ['APP_SETTINGS'])

path_app = path.dirname(path.abspath(__file__))
path_base = path.dirname(path_app)
path_models = path.join(path_base, 'models')
modelzip_bucket = 'comparatory'
modelzip_filename = 'models.zip'
AWS_SECRET_ACCESS_KEY = environ['AWS_SECRET_ACCESS_KEY']
AWS_ACCESS_KEY_ID = environ['AWS_ACCESS_KEY_ID']
