from django.contrib import admin

from multilingual_model import settings
MAX_LANGUAGES = len(settings.LANGUAGES)

class TranslationInline(admin.StackedInline):
    extra = 1
    min_num = 1
    max_num = MAX_LANGUAGES

