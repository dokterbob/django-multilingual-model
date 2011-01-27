from django.contrib import admin

from multilingual_model.forms import TranslationFormSet
from multilingual_model import settings
MAX_LANGUAGES = len(settings.LANGUAGES)


class TranslationInline(admin.StackedInline):
    extra = 1
    formset = TranslationFormSet
    max_num = MAX_LANGUAGES
