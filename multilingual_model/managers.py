from django.db import models


class TranslationQuerySetMixin(object):
    """
    Mixin to allow for using translation functionality with custom Managers
    and/or QuerySets.
    """

    def with_translations(self):
        """
        Return a queryset for which translations have been prefetched,
        optionally filtering for a specific language code is done.
        """

        return self.prefetch_related('translations')

    def translated_to(self, languages):
        """
        Return only objects translated into the specified language code or
        list of language codes.

        Note: In order to prevent duplicate results, the distinct() method
        has been applied after filtering, assuring that only objects with
        all fields equal are returned.
        """

        # If it's a single string, change into a list
        if isinstance(languages, basestring):
            languages = [languages]

        qs = self.filter(translations__language_code__in=languages)

        # Because there is no GROUP BY support in Django, a distinct is
        # required. This *might* create unexpected results though.
        qs = qs.distinct()

        return qs


class TranslationQuerySet(TranslationQuerySetMixin, models.query.QuerySet):
    """ Custom QuerySet for performing optimized translation queries. """

    pass


class MultilingualModelManager(models.Manager):
    """ Manager for generating optimized TranslationQuerySet. """

    def get_query_set(self):
        return TranslationQuerySet(self.model, using=self._db)

    def with_translations(self):
        return self.get_query_set().with_translations()

    def translated_to(self, languages):
        return self.get_query_set().translated_to(languages)
