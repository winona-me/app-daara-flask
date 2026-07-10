import os

class BaseConfig:
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-moi')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
    'DEV_DATABASE_URL',
    'postgresql+psycopg2://postgres:root@localhost:5432/daara'
)

class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}