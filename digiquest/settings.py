import os
from dotenv import load_dotenv
from pathlib import Path
from django.core.mail import send_mail

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["dc4f-2405-201-6001-c9b3-e502-40c2-b97f-8ed2.ngrok-free.app","192.168.82.120",'127.0.0.1','localhost','192.168.29.222','192.168.29.221','0.0.0.0','192.168.29.157','192.168.82.120','192.168.29.121', '192.168.29.82','192.168.29.72','192.168.29.242','localhost','192.168.29.252','192.168.29.103']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework_simplejwt',
    'rest_framework',
    'corsheaders',
    'doctor',
    'patient',
    'subdoctor',
    'clinic',
    'reception',
    'doctorappointment',
    'patientappointment',
    'digiadmin',
    'django_celery_results',
]


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')




REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

from datetime import timedelta


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=2),
}

BASE_DIRT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEOIP_PATH =os.path.join('geoip')



MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'digiquest.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'digiquest.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    '/home/poweruser/Desktop/PRODUCTION/digiquest/static',
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# This is optional but often used in production to collect all static files
BASE_DIR = Path(__file__).resolve().parent.parent
 
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',  
    'http://192.168.29.221:8000',
    'http://127.0.0.1:3000',
]


CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS',
]


import os
import logging
from logging.handlers import RotatingFileHandler


log_dir_doctor = BASE_DIR / 'doctor' / 'doctorlogs'
log_dir_patient= BASE_DIR / 'patient' /'patientlogs'
log_dir_subdoctor= BASE_DIR / 'subdoctor' / 'subdoctorlogs'
log_dir_patientappointment= BASE_DIR / 'patientappointment' / 'patientappointmentlogs'
log_dir_doctorappointment= BASE_DIR / 'doctorappointment' / 'doctorappointmentlogs'
log_dir_reception= BASE_DIR / 'reception' / 'receptionlogs'
log_dir_clinic= BASE_DIR /'clinic'/'cliniclogs'

if not os.path.exists(log_dir_doctor):
    os.makedirs(log_dir_doctor)

if not os.path.exists(log_dir_patient):
    os.makedirs(log_dir_patient)

if not os.path.exists(log_dir_subdoctor):
    os.makedirs(log_dir_subdoctor)
    
if not os.path.exists(log_dir_patientappointment):   
    os.makedirs(log_dir_patientappointment)

if not os.path.exists(log_dir_doctorappointment):    
    os.makedirs(log_dir_doctorappointment)
    
if not os.path.exists(log_dir_reception):
    os.makedirs(log_dir_reception)
    
if not os.path.exists(log_dir_clinic):
    os.makedirs(log_dir_clinic)

# Define the logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'ERROR_FILE_DOCTOR': {
            'level': 'ERROR', 
            'class': 'logging.FileHandler',
            'filename': os.path.join(log_dir_doctor, 'error.log'),
            'formatter': 'custom_format', 
        },
        'WARNING_FILE_DOCTOR': {
            'level': 'WARNING', 
            'class': 'logging.FileHandler',
            'filename': os.path.join(log_dir_doctor, 'warning.log'),
            'formatter': 'custom_format',
        },
        'INFO_FILE_DOCTOR': {
            'level': 'INFO', 
            'class': 'logging.FileHandler',
            'filename': os.path.join(log_dir_doctor, 'info.log'),
            'formatter': 'custom_format',
        },
        'ERROR_FILE_PATIENT': {
            'level': 'ERROR', 
            'class': 'logging.FileHandler',
            'filename': os.path.join(log_dir_patient, 'error.log'),
            'formatter': 'custom_format', 
        },
        'WARNING_FILE_PATIENT': {
            'level': 'WARNING', 
            'class': 'logging.FileHandler',
            'filename': os.path.join(log_dir_patient, 'warning.log'),
            'formatter': 'custom_format',
        },
        'INFO_FILE_PATIENT': {
            'level': 'INFO', 
            'class': 'logging.FileHandler',
            'filename': os.path.join(log_dir_patient, 'info.log'),
            'formatter': 'custom_format',
        },
        'ERROR_FILE_SUBDOCTOR': {
            'level': 'ERROR', 
            'class': 'logging.FileHandler',
            'filename': os.path.join(log_dir_subdoctor, 'error.log'),
            'formatter': 'custom_format', 
        },
        'WARNING_FILE_SUBDOCTOR': {
            'level': 'WARNING', 
            'class': 'logging.FileHandler',
            'filename': os.path.join(log_dir_subdoctor, 'warning.log'),
            'formatter': 'custom_format',
        },
        'INFO_FILE_SUBDOCTOR': {
            'level': 'INFO', 
            'class': 'logging.FileHandler',
            'filename': os.path.join(log_dir_subdoctor, 'info.log'),
            'formatter': 'custom_format',
        },
        'ERROR_FILE_PATIENTAPPOINTMENT': {
            'level': 'ERROR', 
            'class': 'logging.FileHandler',
            'filename': os.path.join(log_dir_patientappointment, 'error.log'),
            'formatter': 'custom_format', 
        },
        'WARNING_FILE_PATIENTAPPOINTMENT': {
            'level': 'WARNING', 
            'class': 'logging.FileHandler',
            'filename': os.path.join(log_dir_patientappointment, 'warning.log'),
            'formatter': 'custom_format',
        },
        'INFO_FILE_PATIENTAPPOINTMENT': {
            'level': 'INFO', 
            'class': 'logging.FileHandler',
            'filename': os.path.join(log_dir_patientappointment, 'info.log'),
            'formatter': 'custom_format',
        },
        'ERROR_FILE_DOCTORAPPOINTMENT': {
            'level': 'ERROR', 
            'class': 'logging.FileHandler',
            'filename': os.path.join(log_dir_doctorappointment, 'error.log'),
            'formatter': 'custom_format', 
        },
        'WARNING_FILE_DOCTORAPPOINTMENT': {
            'level': 'WARNING', 
            'class': 'logging.FileHandler',
            'filename': os.path.join(log_dir_doctorappointment, 'warning.log'),
            'formatter': 'custom_format',
        },
        'INFO_FILE_DOCTORAPPOINTMENT': {
            'level': 'INFO', 
            'class': 'logging.FileHandler',
            'filename': os.path.join(log_dir_doctorappointment, 'info.log'),
            'formatter': 'custom_format',
        },
        'ERROR_FILE_RECEPTION': {
            'level': 'ERROR', 
            'class': 'logging.FileHandler',
            'filename': os.path.join(log_dir_reception, 'error.log'),
            'formatter': 'custom_format', 
        },
        'WARNING_FILE_RECEPTION': {
            'level': 'WARNING', 
            'class': 'logging.FileHandler',
            'filename': os.path.join(log_dir_reception, 'warning.log'),
            'formatter': 'custom_format',
        },
        'INFO_FILE_RECEPTION': {
            'level': 'INFO', 
            'class': 'logging.FileHandler',
            'filename': os.path.join(log_dir_reception, 'info.log'),
            'formatter': 'custom_format',
        },
        'ERROR_FILE_CLINIC': {
            'level': 'ERROR', 
            'class': 'logging.FileHandler',
            'filename': os.path.join(log_dir_clinic, 'error.log'),
            'formatter': 'custom_format', 
        },
        'WARNING_FILE_CLINIC': {
            'level': 'WARNING', 
            'class': 'logging.FileHandler',
            'filename': os.path.join(log_dir_clinic, 'warning.log'),
            'formatter': 'custom_format',
        },
        'INFO_FILE_CLINIC': {
            'level': 'INFO', 
            'class': 'logging.FileHandler',
            'filename': os.path.join(log_dir_clinic, 'info.log'),
            'formatter': 'custom_format',
        },
    },
    'formatters': {
        'custom_format': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s',
        },
    },
    'loggers': {
        'error_doctor': {
            'handlers': ['ERROR_FILE_DOCTOR'],
            'level': 'ERROR',
            'propagate': False,  # Prevent propagation to root logger
        },
        'warning_doctor': {
            'handlers': ['WARNING_FILE_DOCTOR'],
            'level': 'WARNING',
            'propagate': False,  # Prevent propagation to root logger
        },
        'info_doctor': {
            'handlers': ['INFO_FILE_DOCTOR'],
            'level': 'INFO',
            'propagate': False,  # Prevent propagation to root logger
        },
        'error_patient': {
            'handlers': ['ERROR_FILE_PATIENT'],
            'level': 'ERROR',
            'propagate': False,  # Prevent propagation to root logger
        },
        'warning_patient': {
            'handlers': ['WARNING_FILE_PATIENT'],
            'level': 'WARNING',
            'propagate': False,  # Prevent propagation to root logger
        },
        'info_patient': {
            'handlers': ['INFO_FILE_PATIENT'],
            'level': 'INFO',
            'propagate': False,  # Prevent propagation to root logger
        },
        'error_subdoctor': {
            'handlers': ['ERROR_FILE_SUBDOCTOR'],
            'level': 'ERROR',
            'propagate': False,  # Prevent propagation to root logger
        },
        'warning_subdoctor': {
            'handlers': ['WARNING_FILE_SUBDOCTOR'],
            'level': 'WARNING',
            'propagate': False,  # Prevent propagation to root logger
        },
        'info_subdoctor': {
            'handlers': ['INFO_FILE_SUBDOCTOR'],
            'level': 'INFO',
            'propagate': False,  # Prevent propagation to root logger
        },
        'error_patientappointment': {
            'handlers': ['ERROR_FILE_PATIENTAPPOINTMENT'],
            'level': 'ERROR',
            'propagate': False,  # Prevent propagation to root logger
        },
        'warning_patientappointment': {
            'handlers': ['WARNING_FILE_PATIENTAPPOINTMENT'],
            'level': 'WARNING',
            'propagate': False,  # Prevent propagation to root logger
        },
        'info_patientappointment': {
            'handlers': ['INFO_FILE_PATIENTAPPOINTMENT'],
            'level': 'INFO',
            'propagate': False,  # Prevent propagation to root logger
        },
        'error_doctorappointment': {
            'handlers': ['ERROR_FILE_DOCTORAPPOINTMENT'],
            'level': 'ERROR',
            'propagate': False,  # Prevent propagation to root logger
        },
        'warning_doctorappointment': {
            'handlers': ['WARNING_FILE_DOCTORAPPOINTMENT'],
            'level': 'WARNING',
            'propagate': False,  # Prevent propagation to root logger
        },
        'info_doctorappointment': {
            'handlers': ['INFO_FILE_DOCTORAPPOINTMENT'],
            'level': 'INFO',
            'propagate': False,  # Prevent propagation to root logger
        },
        'error_reception': {
            'handlers': ['ERROR_FILE_RECEPTION'],
            'level': 'ERROR',
            'propagate': False,  # Prevent propagation to root logger
        },
        'warning_reception': {
            'handlers': ['WARNING_FILE_RECEPTION'],
            'level': 'WARNING',
            'propagate': False,  # Prevent propagation to root logger
        },
        'info_reception': {
            'handlers': ['INFO_FILE_RECEPTION'],
            'level': 'INFO',
            'propagate': False,  # Prevent propagation to root logger
        },
        'error_clinic': {
            'handlers': ['ERROR_FILE_CLINIC'],
            'level': 'ERROR',
            'propagate': False,  # Prevent propagation to root logger
        },
        'warning_clinic': {
            'handlers': ['WARNING_FILE_CLINIC'],
            'level': 'WARNING',
            'propagate': False,  # Prevent propagation to root logger
        },
        'info_clinic': {
            'handlers': ['INFO_FILE_CLINIC'],
            'level': 'INFO',
            'propagate': False,  # Prevent propagation to root logger
        },
    },
}





















from celery.schedules import crontab

CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Kolkata'
CELERY_RESULT_BACKEND = 'django-db'

# from datetime import timedelta

# CELERY_BEAT_SCHEDULE = {
#     'check-trial-expiry-every-3-seconds': {
#         'task': 'doctor.tasks.check_trial_expiry',  # Correct path based on your structure
#         'schedule': timedelta(seconds=3),  # Correct usage of timedelta
#     },
# }

from datetime import timedelta

CELERY_BEAT_SCHEDULE = {
    'send-appointment-reminders-every-minute': {
        'task': 'doctorappointment.tasks.send_appointment_reminders',
        'schedule': timedelta(seconds=5),  # Change to 1 minute for testing
    },
}
