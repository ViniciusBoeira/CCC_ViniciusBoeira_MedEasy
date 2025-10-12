import os

class Config(object):
    """
    Configuração base, para todos os ambientes.
    """
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://meduser:password@localhost:5432/medeasy')
    BOOTSTRAP_FONTAWESOME = True
    SECRET_KEY = os.environ.get('SECRET_KEY', 'password')
    CSRF_ENABLED = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
class ProductionConfig(Config):
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'