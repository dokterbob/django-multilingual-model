from django.db import connections
from django.utils.translation import ugettext_lazy as _
from django.forms.models import BaseInlineFormSet
from django import forms

from multilingual_model import settings


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

        if len(self.forms) > 0:
            # If a default language has been provided, make sure a translation
            # is available

            if settings.DEFAULT_LANGUAGE and not any(self.errors):
                # Don't bother validating the formset unless each form is valid on its own
                # http://docs.djangoproject.com/en/dev/topics/forms/formsets/#custom-formset-validation

                default_translation_available = False

                for form in self.forms:
                    if form.cleaned_data.get('language_code', None) \
                            == settings.DEFAULT_LANGUAGE:
                        default_translation_available = True
                        break

                    if not default_translation_available:
                        raise forms.ValidationError(_('No translation \
                                provided for default language \'%s\'.') \
                                % settings.DEFAULT_LANGUAGE)

        else:
            raise forms.ValidationError(_('At least one translation should be provided.'))

    def _construct_available_languages(self):
        self.available_languages = [choice[0] \
            for choice in self.form.base_fields['language_code'].choices
            if choice[0] != '']

    def _construct_forms(self):
        """
        Before we're constructing forms, make sure a complete list of
        languages is available. This is used to select sensible defaults
        for the language_code field.
        """

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


        if settings.DEFAULT_LANGUAGE \
                and settings.DEFAULT_LANGUAGE in self.available_languages:
            # Default language still available

            self.available_languages.remove(settings.DEFAULT_LANGUAGE)
            return settings.DEFAULT_LANGUAGE

        else:
            # Select the first item and return it
            return self.available_languages.pop(0)

    def _construct_form(self, i, **kwargs):
        """
        This code has been taken literally from the superclass, as it seemed
        not possible to make initials depend on the values of the
        language code for instanaces.
        """

        if self.is_bound and i < self.initial_form_count():
            pk_key = "%s-%s" % (self.add_prefix(i), self.model._meta.pk.name)
            pk = self.data[pk_key]
            pk_field = self.model._meta.pk
            pk = pk_field.get_db_prep_lookup('exact', pk,
                connection=connections[self.get_queryset().db])
            if isinstance(pk, list):
                pk = pk[0]
            kwargs['instance'] = self._existing_object(pk)
        if i < self.initial_form_count() and not kwargs.get('instance'):
            kwargs['instance'] = self.get_queryset()[i]

        instance = kwargs.get('instance', None)
        if instance:
            self.available_languages.remove(instance.language_code)
        else:
            kwargs['initial'] = \
                {'language_code': self._get_default_language()}

        return super(BaseInlineFormSet, self)._construct_form(i, **kwargs)
