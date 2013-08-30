from django.contrib import admin

from .forms import TranslationFormSet
from . import settings


class TranslationInline(admin.StackedInline):
    def __init__(self, *args, **kwargs):
        super(TranslationInline, self).__init__(*args, **kwargs)

        if settings.AUTO_HIDE_LANGUAGE:
            self.exclude = ('language_code', )
            self.can_delete = False

    extra = 1
    formset = TranslationFormSet
    max_num = len(settings.LANGUAGES)
