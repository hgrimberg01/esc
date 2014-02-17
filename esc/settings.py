# Django settings for esc project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG
import os

ADMINS = (
     ('Howard Grimberg', 'hgrimberg@ku.edu'),
     ('Aleksander Eskilson', 'aeskilson@ku.edu')
)

MANAGERS = ADMINS

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))


if(DEBUG):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': '/tmp/db.file',  # Or path to database file if using sqlite3.
            'USER': 'expo_dev',  # Not used with sqlite3.
            'PASSWORD': '',  # Not used with sqlite3.
            'HOST': '',  # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '',  # Set to empty string for default. Not used with sqlite3.
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': 'expo_dev',  # Or path to database file if using sqlite3.
            'USER': 'expo_dev',  # Not used with sqlite3.
            'PASSWORD': 'b66f7X33v4v17w8XkYtA7s',  # Not used with sqlite3.
            'HOST': '/var/run/mysqld/mysqld.sock',  # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '3306',  # Set to empty string for default. Not used with sqlite3.
        }
    }



# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_DIR, '..', 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PROJECT_DIR, '..', 'static/')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '*lcmk=vcg4x99f(1(166gd6pjjd@x_!(jkd%!nc(=-kd(k+*lx'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)
ADMIN_MEDIA_PREFIX = ''
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'esc.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'esc.wsgi.application'

TEMPLATE_DIRS = (
                 os.path.join(PROJECT_DIR, '..', 'templates'),
                 )

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.messages',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    'registration',
    'scoring',
    'adminplus',
    'django_twilio',
    'register',

    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)
TWILIO_ACCOUNT_SID = 'AP5b55a1b40fbe65b6ffb093328e82df86'
TWILIO_AUTH_TOKEN = '523d856203389a7695ce0f69445ef616'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/tmp'
    }
}

GLOBAL_SETTINGS = {
    'MAX_NORMAL_SCORE':100.0,
    'MIN_NORMAL_SCORE': 0.0,
    'DECIMAL_PLACES_TO_ROUND':5,
    'SCHOOL_TYPES':(('HS','High School'),('MS','Middle School'),('ES','Elementary School'),('OTH','Other School'),),
    'SCORE_TYPES' : (('STD','Standard'), ('EGD', 'Egg Drop'),('WRKT','Water Rocket'),('GCAR','Gravity Car'),('DMUD','Drilling Mud'), ('SKY','Skyscraper'),
                     ('PBR','Pasta Bridge'),('CCAR','Chemical Car'),('WLFT','Weight Lifting'),('ICT','Indoor Catapults'),)
}
MESSAGE_STORAGE = 'django.contrib.messages.storage.fallback.FallbackStorage'
TEMPLATE_CONTEXT_PROCESSORS = ("django.contrib.auth.context_processors.auth",
"django.core.context_processors.debug",
"django.core.context_processors.i18n",
"django.core.context_processors.media",
"django.core.context_processors.static",
"django.core.context_processors.tz",
"django.contrib.messages.context_processors.messages")


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp-mail.outlook.com'
DEFAULT_FROM_EMAIL='score-system@outlook.com'
EMAIL_HOST_PASSWORD = 'x9R7hhwrLsaccd'

EMAIL_HOST_USER ='score-system@outlook.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_SUBJECT_PREFIX = '[EXPO]'
