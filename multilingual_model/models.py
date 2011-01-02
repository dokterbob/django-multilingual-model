import logging

logger = logging.getLogger('multilingual_model')

from django.db import models
from django.utils.translation import get_language
from django.core.exceptions import ObjectDoesNotExist
import re

# What does this line of code do?
models.options.DEFAULT_NAMES += ('translation', 'multilingual')

from multilingual_model import settings

LANGUAGE_CODE_RE = re.compile(r'_(?P<code>[a-z_]{2,5})$')


class MultilingualTranslation(models.Model):
    """ Abstract base class for translations. """
    
    # TO DO: Somehow make sure that this model contains a FK with related_name='translations'.
    
    class Meta:
        abstract = True
    
    language_code = models.CharField(max_length=5, choices=settings.LANGUAGES, 
                                     blank=False, null=False,
                                     default=settings.DEFAULT_LANGUAGE)


class MultilingualModel(models.Model):
    """Provides support for multilingual fields. """
    
    class Meta:
        abstract = True
        
    def __init__(self, *args, **kwargs):
        super(MultilingualModel, self).__init__(*args, **kwargs)
        self._language = get_language()
    
    def __getattr__(self, attr):
        # If an attribute is defined in the current model, don't look any further.
        if attr in self.__dict__:
            return self.__dict__[attr]
        
        #logger.debug('Looking for a translated field for: %s' % attr)
            
        # See whether we can find a translation for the field
        translated_fields = self.translations.model._meta.get_all_field_names()
        for field in translated_fields:
            code = None
            
            # Only consider attributes starting with this field name
            if attr.startswith(field):
                # If we have a match, see if we can re-match the language code in
                # the remaining string.
                match = LANGUAGE_CODE_RE.match(attr[len(field):])
                if match:
                    code = match.group('code')
                
                    logger.debug('Regular expression match, resulting code: %s' % code)
                
                elif attr in translated_fields:
                    code = self._language
                    field = attr
                
                    logger.debug('Regular expression not matched but translated field detected.')
                
            if code:
                translations = self.translations.select_related()
                
                try:
                    logger.debug('Matched with field %s for language %s. Attempting lookup.' % (field, code))
                     
                    translation_obj = translations.get(language_code=code)
                    field_value = getattr(translation_obj, field)
                    
                    logger.debug('Found translation object %s, returning value %s.' % (translation_obj, field_value))
                    
                    return field_value
                    
                except ObjectDoesNotExist:
                    logger.debug('Lookup failed, attempting fallback or failing silently.')
                    
                    if settings.FALL_BACK_TO_DEFAULT and \
                       settings.DEFAULT_LANGUAGE and \
                       code != settings.DEFAULT_LANGUAGE:
                       
                        try:
                            translation_obj = translations.get(language_code=\
                                                    settings.DEFAULT_LANGUAGE)
                            
                            field_value = getattr(translation_obj, field)
                            
                            logger.debug('Found translation object %s, returning value %s.' % (translation_obj, field_value))
                            
                            return field_value

                        except ObjectDoesNotExist:
                            pass
                    
                    if settings.FAIL_SILENTLY:
                        return None
                    
                    raise ValueError, "'%s' object with pk '%s' has no translation to '%s'" \
                        % (self._meta.object_name, self.pk, code)

        raise AttributeError, "'%s' object has no attribute '%s'" \
            % (self._meta.object_name, str(attr))
    
    def for_language(self, code):
        """Sets the language for the translation fields of this object"""
        
        if code is not None and len(code) >= 2 and len(code) <= 5:
            self._language = code
    
    # def contribute_to_class(self, cls):
    #     logger.debug('Adding foreignkey to translation field')
    # 
    #     backlink = models.ForeignKey(cls)
    #     backlink.contribute_to_class(cls._meta.translation, 'model')
    # 
