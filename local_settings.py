# from settings import PROJECT_ROOT, SITE_ROOT
import os

DEBUG = True
TEMPLATE_DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'hifzdb',
        'USER': 'dummy',
        'PASSWORD': 'dummy',
        'HOST': '',
        'PORT': '',
    }
}
