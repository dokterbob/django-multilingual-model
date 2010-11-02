from django.db import models

from multilingual_model.models import MultilingualModel, MultilingualTranslation

class BookTranslation(MultilingualTranslation):
    parent = models.ForeignKey('Book', related_name='translations')
    
    title = models.CharField(max_length=32)
    description = models.TextField()

class Book(MultilingualModel):
    ISBN = models.IntegerField()

__test__ = {'doctest': """
>>> book = Book(ISBN="1234567890")
>>> book.save()
>>> book_en = BookTranslation(language_code='en')
>>> book_en.title = "Django for Dummies"
>>> book_en.description = "Django described in simple words."
>>> book_en.parent = book
>>> book_en.save()
>>> book_pl = BookTranslation(language_code='pl')
>>> book_pl.title = "Django dla Idiotow"
>>> book_pl.description = "Django opisane w prostych slowach"
>>> book_pl.parent = book
>>> book_pl.save()
>>> # now here comes the magic
>>> book.title_en
u'Django for Dummies'
>>> book.description_pl
u'Django opisane w prostych slowach'
>>> mybook = Book(ISBN=1234)
>>> mybook.save()
>>> trans_en = BookTranslation(parent=mybook, language_code='en', title='Django for dummies', description='Django for absolute nitwits.')
>>> trans_en.save()
>>> trans_nl = BookTranslation(parent=mybook, language_code='nl', title='Django voor dummies', description='Django voor complete idioten.')
>>> trans_nl.save()
>>> mybook.title_nl
u'Django voor dummies'
>>> mybook.title_en
u'Django for dummies'
>>> mybook.description_en 
u'Django for absolute nitwits.'
>>> mybook.description_nl
u'Django voor complete idioten.'

"""}
