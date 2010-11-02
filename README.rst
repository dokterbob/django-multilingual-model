django-multilingual-model
=========================
Django Simple Multilingual Support for Models.

This is strongly based upon an original project by yazzgoth on Google code.
The original can be found at: http://code.google.com/p/django-multilingual-model/

Usage
-----

models.py:

	from multilingual_model.models import MultilingualModel, MultilingualTranslation

	class BookTranslation(MultilingualTranslation):
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
	from django.contrib import admin
	import models

	class BookTranslationInline(admin.StackedInline):
	   model = models.BookTranslation
	   extra = 1
	   min_num = 1


	class BookAdmin(admin.ModelAdmin):
	   list_display = ["ISBN"]
	   inlines = [BookTranslationInline]

	admin.site.register(models.Book, BookAdmin)

