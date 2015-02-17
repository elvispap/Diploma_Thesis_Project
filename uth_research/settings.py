"""
Django settings for uth_research project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
SETTINGS_DIR = os.path.dirname(__file__)
PROJECT_PATH = os.path.join(SETTINGS_DIR, os.pardir)
PROJECT_PATH = os.path.abspath(PROJECT_PATH)

TEMPLATE_PATH = os.path.join(PROJECT_PATH, 'templates')
STATIC_PATH = os.path.join(PROJECT_PATH,'static')

# BASE_DIR = os.path.dirname(os.path.dirname(__file__))
# PROJECT_DIR = os.path.dirname(__file__)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '9k#uy^5e85z%+7$l08$)=#rhdzbud*vp=f)1nqixn%p#q634xb'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = True

# TEMPLATE_DIRS = (
# 	TEMPLATE_PATH,
# )
# TEMPLATE_DIRS = (
#     "C:/Users/Elvis/Desktop/Diplwmatikh/uth_research/uth_research/templates",
# )

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), 'templates').replace('\\','/'),
)
ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app',
    'pagination',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'pagination.middleware.PaginationMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "django.core.context_processors.static")

ROOT_URLCONF = 'uth_research.urls'

WSGI_APPLICATION = 'uth_research.wsgi.application'


# Databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'uth_research_db_2',
        'USER': 'root', 
        'PASSWORD': '******',
        'HOST': 'localhost',
        'PORT': '',
    },
    'uth_research_central_db': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'uth_research_central_db',
        'USER': 'root', 
        'PASSWORD': '******',         # must change
        'HOST': 'localhost',        # must change
        'PORT': '',             # must change
    }
}
# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
STATIC_ROOT = '/opt/lampp/apache2/htdocs/static'
STATIC_URL ='http://83.212.97.66/static/'


STATICFILES_DIRS = (
#    #"C:/Users/Elvis/Desktop/Diplwmatikh/uth_research/uth_research/static",
     os.path.join(os.path.dirname(__file__), 'static'),
)
