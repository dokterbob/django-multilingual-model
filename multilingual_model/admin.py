from django.contrib import admin

from multilingual_model.forms import TranslationFormSet
from multilingual_model import settings
MAX_LANGUAGES = len(settings.LANGUAGES)


class TranslationInline(admin.StackedInline):
    def __init__(self, *args, **kwargs):
        super(TranslationInline, self).__init__(*args, **kwargs)

        if settings.AUTO_HIDE_LANGUAGE:
            self.exclude = ('language_code', )

    extra = 1
    formset = TranslationFormSet
    max_num = MAX_LANGUAGES
