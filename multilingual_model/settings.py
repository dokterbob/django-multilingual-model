from django.conf import settings


FAIL_SILENTLY = getattr(
    settings, 'MULTILINGUAL_FAIL_SILENTLY', not settings.DEBUG
)

DEFAULT_LANGUAGE = getattr(
    settings, 'MULTILINGUAL_LANGUAGE_CODE', settings.LANGUAGE_CODE
)

FALL_BACK_TO_DEFAULT = getattr(
    settings, 'MULTILINGUAL_FALL_BACK_TO_DEFAULT', True
)

LANGUAGES = getattr(
    settings, 'MULTILINGUAL_LANGUAGES', settings.LANGUAGES
)

HIDE_LANGUAGE = getattr(
    settings, 'MULTILINGUAL_HIDE_LANGUAGE', len(LANGUAGES) == 1
)
