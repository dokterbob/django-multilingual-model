from django.conf import settings

FAIL_SILENTLY = getattr(settings, 'MULTILINGUAL_FAIL_SILENTLY', not settings.DEBUG)
DEFAULT_LANGUAGE = getattr(settings, 'MULTILINGUAL_DEFAULT', 'en')
FALL_BACK_TO_DEFAULT = getattr(settings, 'MULTILINGUAL_FALL_BACK_TO_DEFAULT', True)
