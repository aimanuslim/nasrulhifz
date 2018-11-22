# from settings import PROJECT_ROOT, SITE_ROOT
import os

DEBUG = True
TEMPLATE_DEBUG = True
SECRET_KEY = 'ui3gi3guigb'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'hifzdb',
        'USER': 'aimanuslim',
        'PASSWORD': 'chanayya211',
        'HOST': '',
        'PORT': '',
    }
}


