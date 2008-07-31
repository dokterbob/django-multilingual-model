from django.db.models import options
import re

options.DEFAULT_NAMES += ('translation', 'multilingual')
MULTILINGUAL_FAIL_SILENTLY = False

class MultilingualModel(models.Model):
    """Provides support for multilingual fields.
    
    Example:
    
    class Language(models.Model):
        code = models.CharField(max_length=5)
        name = models.CharField(max_length=16)
        
    class BookTranslation(models.Model):
        language = models.ForeignKey("Language")
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
        
    def __getattr__(self, attr):
        if attr in self.__dict__:
            return self.__dict__[attr]
        for field in self._meta.multilingual:
            match = re.match(r'^%s_(?P<code>[a-z_]{2,5})$'%field, str(attr))
            if match:
                code = match.groups()[0]
                code = code[:2] # let's limit it to two letters
                try: 
                    return self._meta.translation.objects.select_related().get(model=self, language__code=code).__dict__[field]
                except ObjectDoesNotExist:
                    if MULTILINGUAL_FAIL_SILENTLY:
                        return None
                    break 
            raise AttributeError, "'%s' object has no attribute '%s'"%(self.__class__.__name__, str(attr))
