django-multilingual-model
=========================

.. image:: https://secure.travis-ci.org/dokterbob/django-multilingual-model.png?branch=master
    :target: http://travis-ci.org/dokterbob/django-multilingual-model

Django Simple Multilingual Support for Models
---------------------------------------------

This is strongly based upon an `original project <http://code.google.com/p/django-multilingual-model/>`_ by yazzgoth on Google code.

Usage
-----
When a property of a translation is set for the language currently selected
in this thread, it will automatically yield the right value of that property
for the current language. So for a book which has a tranlation in `en`,
requesting `book.title` from within a template from a client of which the
detected language is English, will simply yield the English translation of the
book title.


models.py::

	from multilingual_model.models import MultilingualModel, MultilingualTranslation

	class BookTranslation(MultilingualTranslation):
	    class Meta:
	        unique_together = ('parent', 'language_code')

	    parent = models.ForeignKey('Book', related_name='translations')

	    title = models.CharField(max_length=32)
	    description = models.TextField()

	class Book(MultilingualModel):
	    ISBN = models.IntegerField()


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

Admin integration
-----------------

admin.py::

	from django.contrib import admin
	import models

	from multilingual_model.admin import TranslationInline


	class BookTranslationInline(TranslationInline):
	   model = models.BookTranslation

	class BookAdmin(admin.ModelAdmin):
	   list_display = ["ISBN"]
	   inlines = [BookTranslationInline]

	admin.site.register(models.Book, BookAdmin)


`__unicode__` representation using translated field
===================================================

In order to make translation of the `__unicode__` function work, some magic
is required. A helper method for this is included by default, allowing you to do the following::

	def __unicode__(self):
	    return self.unicode_wrapper('title', default='Unnamed')
