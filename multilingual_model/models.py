import logging
logger = logging.getLogger('multilingual_model')

import re

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from django.db import models
from django.utils.translation import get_language
from django.core.exceptions import ObjectDoesNotExist

from . import settings

# Match something like en, but also en_us
LANGUAGE_CODE_RE = re.compile(
    r'_(?P<base_code>[a-z]{2,7})(_(?P<ext_code>[a-z]{2,7})){0,1}$'
)


class MultilingualTranslation(models.Model):
    """ Abstract base class for translations. """

    class Meta:
        abstract = True

    language_code = models.CharField(
        _('language'), max_length=7, choices=settings.LANGUAGES,
        blank=False, null=False
    )


class MultilingualModel(models.Model):
    """ Provides support for multilingual fields. """

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(MultilingualModel, self).__init__(*args, **kwargs)
        self._language = get_language()
        self._translation_cache = {}

    def _get_translation(self, field, code):
        """
        Gets the translation of a specific field for a specific language code.

        This raises ObjectDoesNotExist if the lookup was unsuccesful. As of
        today, this stuff is cached. As the cache is rather aggressive it
        might cause rather strange effects. However, we would see the same
        effects when an ordinary object is changed which is already in memory:
        the old state would remain.
        """

        if not code in self._translation_cache:
            translations = self.translations.select_related()

            logger.debug(
                u'Matched with field %s for language %s. Attempting lookup.',
                field, code
            )

            try:
                translation_obj = translations.get(language_code=code)

            except ObjectDoesNotExist:
                translation_obj = None

            self._translation_cache[code] = translation_obj

            logger.debug(u'Translation not found in cache.')

        else:
            logger.debug(u'Translation found in cache.')
            # Get the translation from the cache
            translation_obj = self._translation_cache.get(code)

        # If this is none, it means that a translation does not exist
        # It is important to cache this one as well
        if not translation_obj:
            raise ObjectDoesNotExist

        field_value = getattr(translation_obj, field)

        logger.debug(
            u'Found translation object %s, returning value %s.',
            translation_obj, field_value
        )

        return field_value

    def __getattr__(self, attr):
        # If an attribute is defined in the current model, don't
        # look any further.
        if attr in self.__dict__:
            # TODO: Test coverage!
            return self.__dict__[attr]

        # See whether we can find a translation for the field
        translated_fields = self.translations.model._meta.get_all_field_names()
        for field in translated_fields:
            code = None

            # Only consider attributes starting with this field name
            if attr.startswith(field):
                # If we have a match, see if we can re-match the language
                # code in the remaining string.
                match = LANGUAGE_CODE_RE.match(attr[len(field):])
                if match:
                    base_code = match.group('base_code')
                    ext_code = match.group('ext_code')

                    # TODO: CLEANUP
                    # This is ugly code and redundant.

                    if ext_code:
                        code = '%s-%s' % (base_code, ext_code)
                    else:
                        code = base_code

                    logger.debug(
                        u'Regular expression match, resulting code: %s', code
                    )

                elif attr in translated_fields:
                    # TODO: Test coverage!

                    code = self._language
                    base_code = None
                    field = attr

                    logger.debug(
                        u'Regular expression not matched but translated'
                        u' field detected.'
                    )

            if code:
                try:
                    return self._get_translation(field, code)

                except ObjectDoesNotExist:
                    # TODO: CLEANUP
                    # This is ugly code and redundant.
                    if not base_code:
                        # TODO: Test coverage!
                        base_pos = code.find('-')
                        if base_pos > 0:
                            base_code = code[:base_pos]

                    if base_code:

                        logger.debug(
                            u'Attempting a match for the base \'%s\'',
                            base_code
                        )

                        try:
                            return self._get_translation(field, base_code)
                        except ObjectDoesNotExist:
                            pass

                    logger.debug(
                        u'Lookup failed, attempting fallback or '
                        u'failing silently.'
                    )

                    # If we're using a default language and the current
                    # language is not the default language (which has already
                    # been checked), lookup the value for the default language.
                    if (
                        settings.FALL_BACK_TO_DEFAULT and
                        settings.DEFAULT_LANGUAGE and
                        code != settings.DEFAULT_LANGUAGE
                    ):

                        try:
                            return self._get_translation(
                                field, settings.DEFAULT_LANGUAGE
                            )

                        except ObjectDoesNotExist:
                            # TODO: Test coverage!
                            pass

                    # TODO: Test coverage!
                    if settings.FAIL_SILENTLY:
                        return None

                    raise ValueError(
                        u"'%s' object with pk '%s' has no"
                        u" translation to '%s'" % (
                            self._meta.object_name, self.pk, code
                        )
                    )

        raise AttributeError(
            u"'%s' object has no attribute '%s'" % (
                self._meta.object_name, str(attr)
            )
        )

    def unicode_wrapper(self, property, default=ugettext('Untitled')):
        """
        Wrapper to allow for easy unicode representation of an object by
        the specified property. If this wrapper is not able to find the
        right translation of the specified property, it will return the
        default value instead.

        Example::
            def __unicode__(self):
                return unicode_wrapper('name', default='Unnamed')

        """
        # TODO: Test coverage!
        try:
            value = getattr(self, property)
        except ValueError:
            logger.warn(
                u'ValueError rendering unicode for %s object.',
                self._meta.object_name
            )

            value = None

        if not value:
            value = default

        return value
