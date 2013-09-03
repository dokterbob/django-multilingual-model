import warnings

from django.contrib import admin

from .forms import TranslationFormSet
from . import settings


class TranslationInlineMixin(object):
    def __init__(self, *args, **kwargs):
        super(TranslationInlineMixin, self).__init__(*args, **kwargs)

        if settings.HIDE_LANGUAGE:
            self.exclude = ('language_code', )
            self.can_delete = False

    extra = 1
    formset = TranslationFormSet
    max_num = len(settings.LANGUAGES)


class TranslationStackedInline(TranslationInlineMixin, admin.StackedInline):
    pass


class TranslationTabularInline(TranslationInlineMixin, admin.TabularInline):
    pass


class TranslationInline(TranslationStackedInline):
    def __init__(self, *args, **kwargs):
        warnings.warn(DeprecationWarning(
            "TranslationInline is deprecated; "
            "use TranslationStackedInline or TranslationTabularInline instead."
        ))

        return super(TranslationInline, self).__init__(*args, **kwargs)
