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
"""}
