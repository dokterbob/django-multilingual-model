from django.db import models
from django.utils.translation import get_language
from django.core.exceptions import ObjectDoesNotExist
import re

# What does this line of code do?
models.options.DEFAULT_NAMES += ('translation', 'multilingual')

from multilingual_model import settings

class MultilingualTranslation(models.Model):
    class Meta:
        abstract = True
    
    language_code = models.CharField(max_length=5, choices=settings.LANGUAGES)

class MultilingualModel(models.Model):
    """Provides support for multilingual fields.
    
    Example:
        
    class BookTranslation(MultilingualTranslation):
        title = models.CharField(max_length=32)
        description = models.TextField()
        model = models.ForeignKey("Book")
        
    class Book(MultilingualModel):
        ISBN = models.IntegerField()
        
        class Meta:
            translation = BookTranslation
            multilingual = ['title', 'description']
            
    lang_en = Language(code="en", name="English")
    lang_en.save()
    lang_pl = Language(code="pl", name="Polish")
    book = Book(ISBN="1234567890")
    book.save()
    book_en = BookTranslation()
    book_en.title = "Django for Dummies"
    book_en.description = "Django described in simple words."
    book_en.model = book
    book_en.save()
    book_pl = BookTranslation()
    book_pl.title = "Django dla Idiotow"
    book_pl.description = "Django opisane w prostych slowach"
    book_pl.model = book
    book_pl.save()
    
    # now here comes the magic
    book.title_en
    u'Django for Dummies'
    book.description_pl
    u'Django opisane w prostych slowach'
    """
    class Meta:
        abstract = True
        
    def __init__(self, *args, **kwargs):
        super(MultilingualModel, self).__init__(*args, **kwargs)
        self._language = get_language()[:2]
    
    def __getattr__(self, attr):
        if attr in self.__dict__:
            return self.__dict__[attr]
        for field in self._meta.multilingual:
            code = None
            match = re.match(r'^%s_(?P<code>[a-z_]{2,5})$' % field, str(attr))
            if match:
                code = match.groups('code')
                code = code[:2] # let's limit it to two letter
            elif attr in self._meta.multilingual:
                code = self._language
                field = attr
            if code is not None:
                try: 
                    return self._meta.translation.objects.select_related().get(model=self, language_code=code).__dict__[field]
                except ObjectDoesNotExist:
                    if settings.FALL_BACK_TO_DEFAULT and settings.DEFAULT_LANGUAGE and code != settings.DEFAULT_LANGUAGE:
                        try:
                            return self._meta.translation.objects.select_related().get(model=self, language_code=MULTILINGUAL_DEFAULT).__dict__[field]
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
        
    
