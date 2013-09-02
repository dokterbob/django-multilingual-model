from django.db import models
from django.test import TestCase
from django.utils import translation

from .models import MultilingualModel, MultilingualTranslation


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
>>> trans_en = BookTranslation(parent=mybook, language_code='en', \
    title='Django for dummies', description='Django for absolute nitwits.')
>>> trans_en.save()
>>> trans_nl = BookTranslation(parent=mybook, language_code='nl', \
    title='Django voor dummies', description='Django voor complete idioten.')
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


class BookTestCase(TestCase):
    def setUp(self):
        """ Setup a book with translations. """

        self.book = Book(ISBN="1234567890")
        self.book.save()

        self.book_en = BookTranslation(language_code='en')
        self.book_en.title = "Django for Dummies"
        self.book_en.description = "Django described in simple words."
        self.book_en.parent = self.book
        self.book_en.save()

        self.book_en_us = BookTranslation(language_code='en-us')
        self.book_en_us.title = "Django for Dumbo's"
        self.book_en_us.description = "Django described in simple woords."
        self.book_en_us.parent = self.book
        self.book_en_us.save()

        self.book_pl = BookTranslation(language_code='pl')
        self.book_pl.title = "Django dla Idiotow"
        self.book_pl.description = "Django opisane w prostych slowach"
        self.book_pl.parent = self.book
        self.book_pl.save()

    def test_explicit(self):
        """
        Test explicit request for a specific language. This is basically
        a mockup of the original docstring test.
        """

        self.assertEquals(self.book.title_en, self.book_en.title)
        self.assertEquals(self.book.title_pl, self.book_pl.title)

    def test_language_detection(self):
        """
        Set the language to 'pl' and test whether this is detected from
        within the model.
        """

        for test_lang in ('pl', 'en'):
            # Set the language
            translation.activate(test_lang)

            # Get the book
            book = Book.objects.get(ISBN=self.book.ISBN)

            # Check if the language set in book's init is actually the right
            # language.
            self.assertEquals(book._language, test_lang)

    def test_base_locale_default(self):
        """
        Explicitly request the title in a specific sublocale (en-us) and
        check whether we will get the available base locale instead.
        """

        # assert equality of self.book_en.title and self.book.title_en_us
        self.assertEquals(self.book_en.title, self.book.title_en_kk)

    def test_base_locale_explicit(self):
        """
        Test whether we can explicitly get the value of a string in
        a specific sub-locale - through something like book.title_en_us.
        """

        # Assert equality of book.title_en_us to this unique value
        self.assertEqual(self.book.title_en_us, self.book_en_us.title)

    def test_nonexisting_field(self):
        """
        Check whether requesting an unknown field actually raises an
        AttributeError.
        """

        # assert an exception for self.book.bananas
        with self.assertRaises(AttributeError):
            self.book.bananas

    def test_nonexisting_translation(self):
        """
        Test whether requesting a non-existing translation (when no
        default translation has been used) raises an AttributeError. If
        `FALL_BACK_TO_DEFAULT` and `DEFAULT_LANGUAGE` have been specified -
        chekc if we're actually returning the default.
        """

        # Only do this if no default translation has been defined
        from multilingual_model import settings

        if settings.FALL_BACK_TO_DEFAULT and settings.DEFAULT_LANGUAGE:
            # See if we're given the default language

            result = self.book.title_dk

            attribute = \
                'title_%s' % settings.DEFAULT_LANGUAGE.replace('-', '_')

            self.assertEqual(getattr(self.book, attribute), result)

        else:
            # No defaults have been specifed

            # assert an exception for self.book.title_kk
            with self.assertRaises(AttributeError):
                self.book.title_dk

    def test_serbian_latin(self):
        """ Test for language code edge case. """

        test_lang = 'sr-latn'

        book_translation = BookTranslation(language_code=test_lang)
        book_translation.title = "Django dla Idiotow"
        book_translation.description = "Django opisane w prostych slowach"
        book_translation.parent = self.book
        book_translation.save()

        # Set the language
        translation.activate(test_lang)

        # Get the book
        book = Book.objects.get(ISBN=self.book.ISBN)

        # Check if the language set in book's init is actually the right
        # language.
        self.assertEquals(book._language, test_lang)
