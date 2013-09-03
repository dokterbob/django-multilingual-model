import logging

logger = logging.getLogger(__name__)

from django.utils.translation import ugettext_lazy as _
from django.forms.models import BaseInlineFormSet
from django import forms

from . import settings


class TranslationFormSet(BaseInlineFormSet):
    """
    FormSet for TranslationInlines, making sure that at least one translation
    is required and that sensible default values are selected for the language
    choice.
    """

    def clean(self):
        """
        Make sure there is at least a translation has been filled in. If a
        default language has been specified, make sure that it exists amongst
        translations.
        """

        # First make sure the super's clean method is called upon.
        super(TranslationFormSet, self).clean()

        if settings.HIDE_LANGUAGE:
            return

        if len(self.forms) > 0:
            # If a default language has been provided, make sure a translation
            # is available

            if settings.DEFAULT_LANGUAGE and not any(self.errors):
                # Don't bother validating the formset unless each form is
                # valid on its own. Reference:
                # http://docs.djangoproject.com/en/dev/topics/forms/formsets/#custom-formset-validation

                for form in self.forms:
                    language_code = form.cleaned_data.get(
                        'language_code', None
                    )

                    if language_code == settings.DEFAULT_LANGUAGE:

                        # All is good, don't bother checking any further
                        return

                raise forms.ValidationError(_(
                    'No translation provided for default language \'%s\'.'
                ) % settings.DEFAULT_LANGUAGE)

        else:
            raise forms.ValidationError(
                _('At least one translation should be provided.')
            )

    def _construct_available_languages(self):
        self.available_languages = [
            choice[0]
            for choice in self.form.base_fields['language_code'].choices
            if choice[0] != ''
        ]

    def _construct_forms(self):
        """
        Before we're constructing forms, make sure a complete list of
        languages is available. This is used to select sensible defaults
        for the language_code field.
        """
        if not settings.HIDE_LANGUAGE:
            self._construct_available_languages()

        super(TranslationFormSet, self)._construct_forms()

    def _get_default_language(self):
        """
        If a default language has been set, and is still available in
        `self.available_languages`, return it and remove it from the list.

        If not, simply pop the first available language.
        """

        assert hasattr(self, 'available_languages'), \
            'No available languages have been generated.'
        assert len(self.available_languages) > 0, \
            'No available languages to select from.'

        if (
            settings.DEFAULT_LANGUAGE and
            settings.DEFAULT_LANGUAGE in self.available_languages
        ) or (
            'language_code' not in self.form.base_fields
        ):
            # Default language still available

            self.available_languages.remove(settings.DEFAULT_LANGUAGE)
            return settings.DEFAULT_LANGUAGE

        else:
            # Select the first item and return it
            return self.available_languages.pop(0)

    def _construct_form(self, i, **kwargs):
        """
        Construct the form, overriding the initial value for `language_code`.
        """
        form = super(TranslationFormSet, self)._construct_form(i, **kwargs)

        if settings.HIDE_LANGUAGE:
            form.instance.language_code = settings.DEFAULT_LANGUAGE
        else:
            language_code = form.instance.language_code

            if language_code:
                logger.debug(
                    u'Removing translation choice %s for instance %s'
                    u' in form %d', language_code, form.instance, i
                )

                self.available_languages.remove(language_code)

            else:
                initial_language_code = self._get_default_language()

                logger.debug(
                    u'Preselecting language code %s for form %d',
                    initial_language_code, i
                )

                form.initial['language_code'] = initial_language_code

        return form
