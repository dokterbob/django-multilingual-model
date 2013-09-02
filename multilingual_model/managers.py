from django.db import models


class TranslationQuerySetMixin(object):
    """
    Mixin to allow for using translation functionality with custom Managers
    and/or QuerySets.
    """

    def with_translations(self, language_code=None):
        """
        Return a queryset for which translations have been prefetched,
        optionally filtering for a specific language code is done.
        """

        qs = self.prefetch_related('translations')

        # Filter the current language (optional)
        if language_code:
            qs = qs.filter(
                models.Q(translations=None) |
                models.Q(translations__language_code=language_code)
            )

        return qs


class TranslationQuerySet(TranslationQuerySetMixin, models.query.QuerySet):
    """ Custom QuerySet for performing optimized translation queries. """

    pass


class MultilingualModelManager(models.Manager):
    """ Manager for generating optimized TranslationQuerySet. """

    def get_query_set(self):
        return TranslationQuerySet(self.model, using=self._db)

    def with_translations(self, language_code=None):
        return self.get_query_set().with_translations(language_code)
