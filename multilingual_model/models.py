import logging

logger = logging.getLogger('multilingual_model')

from django.db import models
from django.utils.translation import get_language
from django.core.exceptions import ObjectDoesNotExist
import re

# What does this line of code do?
models.options.DEFAULT_NAMES += ('translation', 'multilingual')

from multilingual_model import settings

class MultilingualTranslation(models.Model):
    """ Abstract base class for translations. """
    
    class Meta:
        abstract = True
    
    language_code = models.CharField(max_length=5, choices=settings.LANGUAGES)

class MultilingualModel(models.Model):
    """Provides support for multilingual fields. """
    
    class Meta:
        abstract = True
        
    def __init__(self, *args, **kwargs):
        super(MultilingualModel, self).__init__(*args, **kwargs)
        self._language = get_language()[:2]
    
    def __getattr__(self, attr):
        # If an attribute is defined in the current model, don't look any further.
        if attr in self.__dict__:
            return self.__dict__[attr]
        
        logger.debug('Looking for a translated field for: %s' % attr)
            
        # See whether we can find a translation for the field
        translated_fields = self._meta.translation._meta.get_all_field_names()
        for field in translated_fields:
            # This is inefficient: we have to compile the re's everytime we do this trick
            code = None
            match = re.match(r'^%s_(?P<code>[a-z_]{2,5})$' % field, str(attr))
            if match:
                code = match.group('code')
                code = code[:2] # let's limit it to two letter
                
                logger.debug('Regular expression match, resulting code: %s' % code)
                
            elif attr in translated_fields:
                code = self._language
                field = attr
                
                logger.debug('Regular expression not matched but translated field detected.')
                
            if code:
                try:
                    logger.debug('Matched with field %s for language %s. Attempting lookup.' % (field, code))
                     
                    translation_obj = self._meta.translation.objects.select_related().get(model=self, language_code=code)
                    field_value = translation_obj.__dict__[field]
                    
                    logger.debug('Found translation object %s, returning value %s.' % (translation_obj, field_value))
                    
                    return field_value
                    
                except ObjectDoesNotExist:
                    logger.debug('Lookup failed, attempting fallback or failing silently.')
                    if settings.FALL_BACK_TO_DEFAULT and settings.DEFAULT_LANGUAGE and code != settings.DEFAULT_LANGUAGE:
                        try:
                            return self._meta.translation.objects.select_related().get(model=self, language_code=settings.DEFAULT_LANGUAGE).__dict__[field]
                        except ObjectDoesNotExist:
                            pass
                    if settings.FAIL_SILENTLY:
                        return None
                    raise ValueError, "'%s' has no translation in '%s'"%(self, code)

        raise AttributeError, "'%s' object has no attribute '%s'"%(self.__class__.__name__, str(attr))
    
    def for_language(self, code):
        """Sets the language for the translation fields of this object"""
        if code is not None and len(code) == 2:
            self._language = code
        
    
