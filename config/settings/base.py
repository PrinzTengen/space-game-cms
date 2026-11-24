# ruff: noqa: ERA001, E501
"""Base settings to build other settings files upon."""

import os
import ssl
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent
# space_game/
APPS_DIR = BASE_DIR / "space_game"
env = environ.Env()

READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=False)
if READ_DOT_ENV_FILE:
    # OS environment variables take precedence over variables from .env
    env.read_env(str(BASE_DIR / ".env"))

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool("DJANGO_DEBUG", False)
# Local time zone. Choices are
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# though not all of them may be available with every OS.
# In Windows, this must be set to your system time zone.
TIME_ZONE = "Europe/Berlin"
# https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = "en"
LANGUAGES = [("en", "English"), ("de", "Deutsch")]
# https://docs.djangoproject.com/en/dev/ref/settings/#languages
# from django.utils.translation import gettext_lazy as _
# LANGUAGES = [
#     ('en', _('English')),
#     ('fr-fr', _('French')),
#     ('pt-br', _('Portuguese')),
# ]
# https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1
# https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True
# https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True
# https://docs.djangoproject.com/en/dev/ref/settings/#locale-paths
LOCALE_PATHS = [str(BASE_DIR / "locale")]

# DATABASES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

if os.getenv("DATABASE_URL", default=None):
    DATABASES = {"default": env.db("DATABASE_URL")}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env.str("POSTGRES_DB"),
            "USER": env.str("POSTGRES_USER"),
            "PASSWORD": env.str("POSTGRES_PASSWORD"),
            "HOST": env.str("POSTGRES_HOST", default="postgres"),
            "PORT": env.str("POSTGRES_PORT", default="5432"),
        },
    }

DATABASES["default"]["ATOMIC_REQUESTS"] = True
# https://docs.djangoproject.com/en/stable/ref/settings/#std:setting-DEFAULT_AUTO_FIELD
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# URLS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = "config.urls"
# https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = "config.wsgi.application"

# APPS
# ------------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # "django.contrib.humanize", # Handy template tags
    "django.contrib.admin",
    "django.forms",
]
THIRD_PARTY_APPS = [
    "cms",
    "django_ratelimit",
    "menus",
    "treebeard",
    "sekizai",
    "filer",
    "easy_thumbnails",
    "djangocms_versioning",
    "djangocms_text",
    "djangocms_link",
    "djangocms_transfer",
    "djangocms_frontend",
    "djangocms_frontend.contrib.accordion",
    "djangocms_frontend.contrib.alert",
    "djangocms_frontend.contrib.badge",
    "djangocms_frontend.contrib.card",
    "djangocms_frontend.contrib.carousel",
    "djangocms_frontend.contrib.collapse",
    "djangocms_frontend.contrib.content",
    "djangocms_frontend.contrib.grid",
    "djangocms_frontend.contrib.icon",
    "djangocms_frontend.contrib.image",
    "djangocms_frontend.contrib.jumbotron",
    "djangocms_frontend.contrib.link",
    "djangocms_frontend.contrib.listgroup",
    "djangocms_frontend.contrib.media",
    "djangocms_frontend.contrib.tabs",
    "djangocms_frontend.contrib.utilities",
    "parler",
    "sortedm2m",
    "taggit",
    "meta",
    "djangocms_stories",
    "djangocms_cookie_love",
    "crispy_forms",
    "crispy_bootstrap5",
    "allauth",
    "allauth.account",
    "allauth.mfa",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.discord",
    "django_celery_beat",
    "rest_framework",
    "rest_framework.authtoken",
    "oauth2_provider",
    "corsheaders",
    "drf_spectacular",
]

LOCAL_APPS = [
    "space_game.control",
    "space_game.users",
    "space_game.theme",
    # Your stuff: custom apps go here
]
# https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
# django CMS imports the custom user model while loading its own models.
INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS + THIRD_PARTY_APPS

# MIGRATIONS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#migration-modules
MIGRATION_MODULES = {
    "sites": "space_game.contrib.sites.migrations",
    "djangocms_stories": "space_game.contrib.stories.migrations",
}

# AUTHENTICATION
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#authentication-backends
AUTHENTICATION_BACKENDS = [
    "space_game.control.backends.AdminAuthenticationBackend",
]
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-user-model
AUTH_USER_MODEL = "users.User"
# https://docs.djangoproject.com/en/dev/ref/settings/#login-redirect-url
LOGIN_REDIRECT_URL = "admin:index"
# https://docs.djangoproject.com/en/dev/ref/settings/#login-url
LOGIN_URL = "account_login"

# PASSWORDS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#password-hashers
PASSWORD_HASHERS = [
    # https://docs.djangoproject.com/en/dev/topics/auth/passwords/#using-argon2-with-django
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# MIDDLEWARE
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "space_game.control.ratelimit.StaffRateLimitMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "djangocms_cookie_love.middleware.CookieConsentMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "space_game.control.middleware.StaffMFAMiddleware",
    "cms.middleware.user.CurrentUserMiddleware",
    "cms.middleware.page.CurrentPageMiddleware",
    "cms.middleware.toolbar.ToolbarMiddleware",
    "space_game.theme.middleware.LogbookToolbarMiddleware",
    "cms.middleware.language.LanguageCookieMiddleware",
    "cms.middleware.utils.ApphookReloadMiddleware",
]

# STATIC
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(BASE_DIR / "staticfiles")
# https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = "/static/"
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = [str(APPS_DIR / "static")]
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# MEDIA
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(APPS_DIR / "media")
# https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = "/media/"

# TEMPLATES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # https://docs.djangoproject.com/en/dev/ref/settings/#dirs
        "DIRS": [str(APPS_DIR / "templates")],
        # https://docs.djangoproject.com/en/dev/ref/settings/#app-dirs
        "APP_DIRS": True,
        "OPTIONS": {
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "space_game.users.context_processors.allauth_settings",
                "space_game.theme.context_processors.design_system",
                "cms.context_processors.cms_settings",
                "sekizai.context_processors.sekizai",
                "djangocms_cookie_love.context_processors.cookie_consent",
            ],
        },
    },
]

# https://docs.djangoproject.com/en/dev/ref/settings/#form-renderer
FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

# http://django-crispy-forms.readthedocs.io/en/latest/install.html#template-packs
CRISPY_TEMPLATE_PACK = "bootstrap5"
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"

# FIXTURES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#fixture-dirs
FIXTURE_DIRS = (str(APPS_DIR / "fixtures"),)

# SECURITY
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-httponly
SESSION_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-httponly
CSRF_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/en/dev/ref/settings/#x-frame-options
X_FRAME_OPTIONS = "SAMEORIGIN"

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = env(
    "DJANGO_EMAIL_BACKEND",
    default="django.core.mail.backends.smtp.EmailBackend",
)
# https://docs.djangoproject.com/en/dev/ref/settings/#email-timeout
EMAIL_TIMEOUT = 5

# ADMIN
# ------------------------------------------------------------------------------
# Django Admin URL.
ADMIN_URL = "admin/"
# https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = ['"Nölp Max" <space-game@mail.gg>']
# https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS
# https://cookiecutter-django.readthedocs.io/en/latest/settings.html#other-environment-settings
# Staff password authentication and MFA share the admin login entry point.
MFA_ADAPTER = "space_game.control.security.StaffMFAAdapter"
MFA_SUPPORTED_TYPES = ["totp", "recovery_codes"]
MFA_TOTP_ISSUER = "Space Game Admin"
MFA_ALLOW_UNVERIFIED_EMAIL = True
MFA_TRUST_ENABLED = False
MFA_RECOVERY_CODES_SHOW_ONCE = True

# Per-IP limits for admin, OAuth and MCP (see space_game/control/ratelimit.py).
# Counters live in the default cache (Redis in production).
RATELIMIT_ENABLE = env.bool("DJANGO_RATELIMIT_ENABLE", default=True)
STAFF_RATE_LIMITS = {
    "admin": env("RATELIMIT_ADMIN", default="300/m"),
    "admin-auth": env("RATELIMIT_ADMIN_AUTH", default="10/m"),
    "oauth": env("RATELIMIT_OAUTH", default="30/m"),
    "oauth-register": env("RATELIMIT_OAUTH_REGISTER", default="10/h"),
    "mcp": env("RATELIMIT_MCP", default="120/m"),
    "mcp-auth-failure": env("RATELIMIT_MCP_AUTH_FAILURE", default="30/h"),
}

MCP_BASE_URL = env("MCP_BASE_URL", default="http://localhost:8000").rstrip("/")
MCP_RESOURCE_URL = MCP_BASE_URL + "/mcp"
MCP_UPLOAD_ROOT = BASE_DIR / ".mcp_uploads"
FILER_REMOVE_FILE_VALIDATORS = ["application/octet-stream"]
FILER_ADD_FILE_VALIDATORS = {
    "application/octet-stream": [
        "space_game.control.validators.validate_binary_download",
    ],
}
MCP_MAX_UPLOAD_BYTES = env.int("MCP_MAX_UPLOAD_BYTES", default=512 * 1024 * 1024)
OAUTH2_PROVIDER = {
    "OAUTH2_VALIDATOR_CLASS": "space_game.control.oauth.ManagementOAuthValidator",
    "DCR_ENABLED": True,
    "DCR_REGISTRATION_PERMISSION_CLASSES": [
        "space_game.control.oauth.LimitedRegistration",
    ],
    "PKCE_REQUIRED": True,
    "COMPLIANT_BCP_RFC9700_PKCE_METHOD": True,
    "COMPLIANT_BCP_RFC9700_PASSWORD_GRANT": True,
    "COMPLIANT_BCP_RFC9700_IMPLICIT_GRANT": True,
    "COMPLIANT_BCP_RFC9700_ACCESS_TOKEN_TRANSPORT": True,
    "COMPLIANT_BCP_RFC9700_TOKEN_STORAGE": True,
    "ACCESS_TOKEN_EXPIRE_SECONDS": 3600,
    "ROTATE_REFRESH_TOKEN": True,
    "REFRESH_TOKEN_REUSE_PROTECTION": True,
    "REFRESH_TOKEN_EXPIRE_SECONDS": 7 * 24 * 3600,
    "SCOPES": {
        "mcp:read": "Inhalte lesen",
        "mcp:write": "Inhalte erstellen, bearbeiten und löschen",
        "mcp:publish": "Entwürfe veröffentlichen",
    },
    "DEFAULT_SCOPES": ["mcp:read"],
    "OAUTH2_RESPONSE_TYPES_SUPPORTED": ["code"],
    "OAUTH2_GRANT_TYPES_SUPPORTED": ["authorization_code", "refresh_token"],
    "OAUTH2_TOKEN_ENDPOINT_AUTH_METHODS_SUPPORTED": [
        "none",
        "client_secret_post",
        "client_secret_basic",
    ],
    "OAUTH2_PROTECTED_RESOURCE_IDENTIFIER": MCP_RESOURCE_URL,
    "OAUTH2_PROTECTED_RESOURCE_AUTHORIZATION_SERVERS": [MCP_BASE_URL],
    "ALLOWED_REDIRECT_URI_SCHEMES": [
        "https",
        "http",
    ],  # Custom validator permits HTTP only for loopback callbacks.
    "ALLOW_LOCALHOST_LOOPBACK": True,
}

# LOGGING
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#logging
# See https://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {"level": "INFO", "handlers": ["console"]},
}

REDIS_URL = env("REDIS_URL", default="redis://redis:6379/0")
REDIS_SSL = REDIS_URL.startswith("rediss://")

# Celery
# ------------------------------------------------------------------------------
if USE_TZ:
    # https://docs.celeryq.dev/en/stable/userguide/configuration.html#std:setting-timezone
    CELERY_TIMEZONE = TIME_ZONE
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#std:setting-broker_url
CELERY_BROKER_URL = REDIS_URL
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#redis-backend-use-ssl
CELERY_BROKER_USE_SSL = {"ssl_cert_reqs": ssl.CERT_NONE} if REDIS_SSL else None
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#std:setting-result_backend
CELERY_RESULT_BACKEND = REDIS_URL
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#redis-backend-use-ssl
CELERY_REDIS_BACKEND_USE_SSL = CELERY_BROKER_USE_SSL
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#result-extended
CELERY_RESULT_EXTENDED = True
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#result-backend-always-retry
# https://github.com/celery/celery/pull/6122
CELERY_RESULT_BACKEND_ALWAYS_RETRY = True
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#result-backend-max-retries
CELERY_RESULT_BACKEND_MAX_RETRIES = 10
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#std:setting-accept_content
CELERY_ACCEPT_CONTENT = ["json"]
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#std:setting-task_serializer
CELERY_TASK_SERIALIZER = "json"
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#std:setting-result_serializer
CELERY_RESULT_SERIALIZER = "json"
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#task-time-limit
# TODO: set to whatever value is adequate in your circumstances
CELERY_TASK_TIME_LIMIT = 5 * 60
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#task-soft-time-limit
# TODO: set to whatever value is adequate in your circumstances
CELERY_TASK_SOFT_TIME_LIMIT = 60
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#beat-scheduler
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#worker-send-task-events
CELERY_WORKER_SEND_TASK_EVENTS = True
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#std-setting-task_send_sent_event
CELERY_TASK_SEND_SENT_EVENT = True
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#worker-hijack-root-logger
CELERY_WORKER_HIJACK_ROOT_LOGGER = False
# django-allauth
# ------------------------------------------------------------------------------
ACCOUNT_ALLOW_REGISTRATION = False
# https://docs.allauth.org/en/latest/account/configuration.html
ACCOUNT_LOGIN_METHODS = {"username"}
# https://docs.allauth.org/en/latest/account/configuration.html
ACCOUNT_SIGNUP_FIELDS = ["email*", "username*", "password1*", "password2*"]
# https://docs.allauth.org/en/latest/account/configuration.html
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
# https://docs.allauth.org/en/latest/account/configuration.html
ACCOUNT_ADAPTER = "space_game.users.adapters.AccountAdapter"
# https://docs.allauth.org/en/latest/account/forms.html
ACCOUNT_FORMS = {"signup": "space_game.users.forms.UserSignupForm"}
# https://docs.allauth.org/en/latest/socialaccount/configuration.html
SOCIALACCOUNT_ADAPTER = "space_game.users.adapters.SocialAccountAdapter"
# https://docs.allauth.org/en/latest/socialaccount/configuration.html
SOCIALACCOUNT_FORMS = {"signup": "space_game.users.forms.UserSocialSignupForm"}
# django-compressor
# ------------------------------------------------------------------------------
# https://django-compressor.readthedocs.io/en/latest/quickstart/#installation
INSTALLED_APPS += ["compressor"]
STATICFILES_FINDERS += ["compressor.finders.CompressorFinder"]
# django-rest-framework
# -------------------------------------------------------------------------------
# django-rest-framework - https://www.django-rest-framework.org/api-guide/settings/
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "space_game.control.rest.StaffSessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAdminUser",),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# django-cors-headers - https://github.com/adamchainz/django-cors-headers#setup
CORS_URLS_REGEX = r"^/api/.*$"

# By Default swagger ui is available only to admin user(s). You can change permission classes to change that
# See more configuration options at https://drf-spectacular.readthedocs.io/en/latest/settings.html#settings
SPECTACULAR_SETTINGS = {
    "TITLE": "Space Game API",
    "DESCRIPTION": "Documentation of API endpoints of Space Game",
    "VERSION": "1.0.0",
    "SERVE_PERMISSIONS": ["rest_framework.permissions.IsAdminUser"],
    "SCHEMA_PATH_PREFIX": "/api/",
}
# Your stuff...
# ------------------------------------------------------------------------------
CMS_TEMPLATES = [
    ("cms/home.html", "Space Game — Landingpage"),
    ("cms/default.html", "Standard"),
    ("cms/fullwidth.html", "Full width"),
    ("cms/download.html", "Space Game — Download"),
    ("cms/faq.html", "Space Game — System & FAQ"),
    ("cms/logbook.html", "Space Game — Logbook"),
    ("cms/contributors.html", "Space Game — Contributors"),
]
CMS_LANGUAGES = {
    SITE_ID: [
        {"code": "en", "name": "English", "public": True},
        {"code": "de", "name": "Deutsch", "public": True},
    ],
    "default": {
        "fallbacks": ["en"],
        "redirect_on_fallback": True,
        "hide_untranslated": False,
    },
}
PARLER_LANGUAGES = {
    SITE_ID: ({"code": "en"}, {"code": "de"}),
    "default": {"fallbacks": ["en"], "hide_untranslated": False},
}
THUMBNAIL_PROCESSORS = (
    "easy_thumbnails.processors.colorspace",
    "easy_thumbnails.processors.autocrop",
    "filer.thumbnail_processors.scale_and_crop_with_subject_location",
    "easy_thumbnails.processors.filters",
)
STORIES_AUTO_SETUP = False  # Set up page/apphook content explicitly after migration.
META_USE_SITES = True  # Stories builds image metadata without passing a request.
META_SITE_PROTOCOL = env("META_SITE_PROTOCOL", default="https")
CMS_PAGE_CACHE = False  # Consent and account controls depend on the visitor.
CMS_PLACEHOLDER_CONF = {
    "hero": {"limits": {"SpaceGameHeroPlugin": 1}},
    "contributor_hero": {
        "plugins": ["SpaceGameHeroPlugin", "TextLinkPlugin"],
        "limits": {"SpaceGameHeroPlugin": 1},
    },
    "contributors": {
        "plugins": [
            "SpaceGameContributorsPlugin",
            "SpaceGameContributorPlugin",
            "SpaceGameContributorRolePlugin",
        ],
        "limits": {"SpaceGameContributorsPlugin": 1},
    },
    "support_header": {
        "plugins": ["SpaceGameSupportHeaderPlugin"],
        "limits": {"global": 1},
    },
    "system_requirements": {
        "plugins": ["SpaceGameRequirementsPlugin", "SpaceGameRequirementPlugin"],
    },
    "faq": {"plugins": ["SpaceGameFAQPlugin", "SpaceGameFAQItemPlugin"]},
    "download_header": {
        "plugins": ["SpaceGameDownloadHeaderPlugin"],
        "limits": {"global": 1},
    },
    "download_steps": {
        "plugins": ["SpaceGameDownloadStepsPlugin", "SpaceGameDownloadStepPlugin"],
        "limits": {"SpaceGameDownloadStepsPlugin": 1},
    },
    "launcher": {
        "plugins": ["SpaceGameLauncherPlugin", "SpaceGameLauncherPlatformPlugin"],
        "limits": {"SpaceGameLauncherPlugin": 1},
    },
    "download_sidebar": {"plugins": ["SpaceGameDownloadInfoPlugin"]},
    "logbook_header": {
        "plugins": ["SpaceGameLogbookHeaderPlugin"],
        "limits": {"global": 1},
    },
}
CMS_PLACEHOLDER_CACHE = False
SG_DISCORD_CLIENT_ID = env("DISCORD_CLIENT_ID", default="")
SG_DISCORD_CLIENT_SECRET = env("DISCORD_CLIENT_SECRET", default="")
SOCIALACCOUNT_PROVIDERS = {"discord": {"SCOPE": ["identify"]}}
if SG_DISCORD_CLIENT_ID and SG_DISCORD_CLIENT_SECRET:
    SOCIALACCOUNT_PROVIDERS["discord"]["APP"] = {
        "client_id": SG_DISCORD_CLIENT_ID,
        "secret": SG_DISCORD_CLIENT_SECRET,
        "key": "",
    }
SG_LAUNCHER_URLS = {
    "win": env("SPACE_GAME_WINDOWS_DOWNLOAD_URL", default=""),
    "linux": env("SPACE_GAME_LINUX_DOWNLOAD_URL", default=""),
}
COOKIE_LOVE_COOKIE_SECURE = env.bool("COOKIE_LOVE_COOKIE_SECURE", default=True)
