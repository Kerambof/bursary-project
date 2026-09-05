import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

load_dotenv()

# -----------------------------
# BASE DIRECTORY
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------
# SECURITY
# -----------------------------
SECRET_KEY = 'django-insecure-^dfm4_ym&j!dql3*4u42jf+zw2fcb3i+c44z2s@5%6a@9w#_ut'
ALLOWED_HOSTS = [
    'bursalite.onrender.com',
    '.vercel.app',
    '127.0.0.1',
    'localhost',
]

CSRF_TRUSTED_ORIGINS = [
    'https://*.vercel.app',
]
# -----------------------------
# APPLICATIONS
# -----------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'grappelli',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'storages',

    'bursary',
    
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'admin_templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# -----------------------------
# DATABASE
# -----------------------------
DATABASE_URL = os.environ.get("DATABASE_URL") or "postgresql://postgres.ojnudkjgcuxzarkelags:F42268024k!@aws-0-eu-west-2.pooler.supabase.com:5432/postgres"

DATABASES = {
    "default": dj_database_url.parse(DATABASE_URL, conn_max_age=600, ssl_require=True)
}

# -----------------------------
# PASSWORD VALIDATION
# -----------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# -----------------------------
# INTERNATIONALIZATION
# -----------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# -----------------------------
# -----------------------------
# STATIC FILES
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = False  # production mode

STATIC_URL = '/static/'

# Where collectstatic will put files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Optional: your own static files source folder
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# -----------------------------
# SUPABASE STORAGE (public bucket)
# -----------------------------
# -----------------------------
# SUPABASE STORAGE (public bucket)
# -----------------------------
AWS_ACCESS_KEY_ID = os.environ.get('SUPABASE_S3_ACCESS_KEY')
AWS_SECRET_ACCESS_KEY = os.environ.get('SUPABASE_S3_SECRET_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('SUPABASE_BUCKET_NAME')
AWS_S3_ENDPOINT_URL = os.environ.get('SUPABASE_S3_ENDPOINT')
AWS_S3_REGION_NAME = os.environ.get('SUPABASE_S3_REGION', 'us-east-1')
AWS_S3_ADDRESSING_STYLE = 'path'
AWS_S3_FILE_OVERWRITE = False
AWS_QUERYSTRING_AUTH = False  # public bucket → plain public URLs
AWS_DEFAULT_ACL = 'public-read'

SUPABASE_PROJECT_REF = os.environ.get('SUPABASE_PROJECT_REF')
AWS_S3_CUSTOM_DOMAIN = f"{SUPABASE_PROJECT_REF}.supabase.co/storage/v1/object/public/{AWS_STORAGE_BUCKET_NAME}"

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

# -----------------------------
# DEFAULT PRIMARY KEY
# -----------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_URL = 'student_login'
LOGIN_REDIRECT_URL = 'student_dashboard'
LOGOUT_REDIRECT_URL = 'student_login'

SESSION_COOKIE_AGE = 60 * 60 * 3
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = True

#for email verification and password reset
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_USE_TLS = False


EMAIL_HOST_USER = 'me.bursary@gmail.com'
EMAIL_HOST_PASSWORD = 'wxej ahxo ywgs fgwi'

DEFAULT_FROM_EMAIL = 'me.bursary@gmail.com'