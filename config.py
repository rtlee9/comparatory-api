class Config(object):
    DEBUG = False
    CSRF_ENABLED = True
    S3_DOWNLOAD = False


class ProductionConfig(Config):
    DEBUG = True
    S3_DOWNLOAD = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
