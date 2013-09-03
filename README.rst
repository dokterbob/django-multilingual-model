=========================
django-multilingual-model
=========================

.. image:: https://secure.travis-ci.org/dokterbob/django-multilingual-model.png?branch=master
    :target: http://travis-ci.org/dokterbob/django-multilingual-model

Django Simple Multilingual Support for models
---------------------------------------------

What is it?
===========
An inefficient, minimal and utterly simple approach to model translation based
on foreign key relations and attribute proxying.

The project code is forked from the
`original project <http://code.google.com/p/django-multilingual-model/>`_ by
yazzgoth on Google code.

Usage
=====
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
=================

admin.py::

	from django.contrib import admin
	import models

	from multilingual_model.admin import TranslationStackedInline


	class BookTranslationInline(TranslationStackedInline):
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

Upgrade from previous versions
==============================
If you upgrade from previous versions you need to be aware of two important facts:

1.  The Model MultilingualTranslation in multilingual_model.models has a field
    named "language_code". In prior versions the max_length was set to 5. This has
    been changed to 7 to allow longer language codes to be valid. This
    could break validation in certain situations. A way to reflect this change on
    the level of the database is to manually change the database table of the models
    that are translated.
2.  In admin.py the class TranslationInline has been renamed to
    TranslationStackedInline. TranslationInline will be deprecated soon. Additionally
    to TranslationStackedInline there now is a TranslationTabularInline.

Settings
========
`MULTILINGUAL_FAIL_SILENTLY`
	Return `None` instead of raising a `ValueError` when a translation for the
	current language cannot be found and `MULTILINGUAL_FALL_BACK_TO_DEFAULT` is
	`False`. Defaults to the inverse of `DEBUG`.

`MULTILINGUAL_FALL_BACK_TO_DEFAULT`
	Whether or not to fall back to `MULTILINGUAL_LANGUAGE_CODE` when no translation
	can be found for the currently activated language. Defaults to `True`.

`MULTILINGUAL_LANGUAGE_CODE`
	The default language used when `MULTILINGUAL_FALL_BACK_TO_DEFAULT` is `True`.
	Defaults to `LANGUAGE_CODE`.

`MULTILINGUAL_LANGUAGES`
	Set of languages available for translation. Defaults to `LANGUAGES`.

`MULTILINGUAL_HIDE_LANGUAGE`
	Hide functionality for selecting the language and removing translations in the admin.
	Defaults to `True` when `MULTILINGUAL_LANGUAGES` contains of a single language.

License
=======
This application is released under the GNU Affero General Public License version 3.
