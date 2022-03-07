import os
import dj_database_url
from environmental_variables import *

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'w5c6o7q!ke)2dhc17syb2fgqw@l$#5f5b349@2(&1$&xjry@a6'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'clintad.herokuapp.com', 'www.clintad.com']

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

# For users who want to run ClinTAD locally on their own computer
DATABASES = {
     'default': {
         'ENGINE': 'django.db.backends.sqlite3',
         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
     }
 }

#DONT MESS AROUND THIS LINES
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': os.environ.get('POSTGRES_DATABASE'),
#         'USER': os.environ.get('POSTGRES_USER'),
#         'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
#         'HOST': os.environ.get('POSTGRES_HOST'),
#         'PORT': os.environ.get('POSTGRES_PORT'),
#     }
# }
