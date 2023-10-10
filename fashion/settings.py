# import os

from pathlib import Path
from datetime import timedelta

from celery.schedules import crontab

BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = 'django-insecure-%vy8$8d6$jah0=bk63#fvyr#@)did)1'
# m*ilrwv+6sj-hr=k@kf'

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'imagekit',
    'sendgrid',

    'web',
    'user',
    'shop',
    'customadmin'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'fashion.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'fashion.context_processors.username',
                'shop.context_processors.cart_count',
                'user_profile.context_processors.wallet',
            ],
        },
    },
]

WSGI_APPLICATION = 'fashion.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


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


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True


STATIC_URL = 'static/'

# STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = '/media/'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


AUTH_USER_MODEL = 'user.CustomUser'

# client.set_app_details({"title" : "<YOUR_APP_TITLE>", "version" : "<YOUR_APP_VERSION>"})

RAZORPAY_KEY_ID = 'rzp_test_7Pm5s9hhe2TILm'
RAZORPAY_KEY_SECRET = 'f4SuCsKkP5FXRQHw4Mx7GiQQ'

EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
SENDGRID_API_KEY = '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'


CELERY_BROKER_URL = 'sqla+sqlite:///celery.sqlite3'
CELERY_RESULT_BACKEND = 'db+sqlite:///celery_results.sqlite3'

CELERY_BEAT_SCHEDULE = {
    'apply_category_offers': {
        'task': 'customadmin.tasks.apply_category_offers',
        'schedule': timedelta(seconds=5),
        # 'schedule': crontab(minute=0, hour=0),
    },
    'apply_product_offers': {
        'task': 'customadmin.tasks.apply_product_offers',
        'schedule': timedelta(seconds=5),
        # 'schedule': crontab(minute=0, hour=0),
    },
}

