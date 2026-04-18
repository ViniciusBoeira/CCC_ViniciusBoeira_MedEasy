import os
import secrets # [SEGURANÇA] Importa o módulo secrets da biblioteca padrão do Python,
               # projetado especificamente para gerar valores criptograficamente seguros

class Config(object):
    """
    Configuração base, para todos os ambientes.
    """
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'postgresql://meduser:password@localhost:5432/medeasy'
    )
    BOOTSTRAP_FONTAWESOME = True
    SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_hex(32))
    CSRF_ENABLED = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    # Chave fixa apenas para testes — nunca usar em produção
    SECRET_KEY = 'chave-apenas-para-testes'
    # Desativa CSRF nos testes para não precisar gerar tokens em cada requisição simulada
    WTF_CSRF_ENABLED = False