"""
Django settings for config project.
"""

import os
from pathlib import Path
import dj_database_url
import cloudinary  # 👈 Added for Cloudinary

# -----------------------------
# BASE DIRECTORY
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------
# SECURITY
# -----------------------------
SECRET_KEY = 'django-insecure-^dfm4_ym&j!dql3*4u42jf+zw2fcb3i+c44z2s@5%6a@9w#_ut'
DEBUG = True  # Set False in production!
ALLOWED_HOSTS = ['bursary-project.onrender.com']

# -----------------------------
# APPLICATIONS
# -----------------------------
INSTALLED_APPS = [
    'django.contrib.admin',         # <-- admin MUST come first
    'grappelli',                    # Grappelli after admin
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
   
    'bursary',                      # your app
    'cloudinary',                   # 👈 Added Cloudinary
    'cloudinary_storage',           # 👈 Added Cloudinary storage
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

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # Add template folders here if needed
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
# Works locally (SQLite) and on Render (Postgres)
# -----------------------------
DATABASE_URL = os.environ.get("DATABASE_URL") or "postgresql://bursary_db_32rh_user:zsbe4EYzyi2NwXpL3gd0CoNFQXp7DxJH@dpg-d6bfn7ali9vc73dge3eg-a.virginia-postgres.render.com/bursary_db_32rh"

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
# STATIC FILES
# -----------------------------
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]


# -----------------------------
# CLOUDINARY CONFIGURATION
# -----------------------------
cloudinary.config(
    cloud_name="dmc4zspa0",   # 👈 replace with your Cloudinary Cloud Name
    api_key="543182367999143",         # 👈 replace with your Cloudinary API Key
    api_secret="9WJeoMU4fXyJgo0QPVXvclfGdh0",   # 👈 replace with your Cloudinary API Secret
    secure=True
)

# Use Cloudinary for all uploaded media files
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# -----------------------------
# DEFAULT PRIMARY KEY
# -----------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_URL = 'student_login'
LOGIN_REDIRECT_URL = 'student_dashboard'
LOGOUT_REDIRECT_URL = 'student_login'

# Session expires after 3 hours (in seconds)
SESSION_COOKIE_AGE = 60 * 60 * 3  # 3 hours

# Expire session if browser closes
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Expire if inactive
SESSION_SAVE_EVERY_REQUEST = True
