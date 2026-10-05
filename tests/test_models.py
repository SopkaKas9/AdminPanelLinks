from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from collections_app.models import Collection, CollectionItem


class CollectionModelTests(TestCase):
    def test_valid_slug_is_accepted(self):
        c = Collection(title="Кухня", slug="kitchen-1")
        c.full_clean()

    def test_slug_rejects_invalid_characters(self):
        for bad in ["кухня", "with space", "under_score", "a/b", "a.b"]:
            with self.subTest(slug=bad):
                c = Collection(title="Тест", slug=bad)
                with self.assertRaises(ValidationError):
                    c.full_clean()

    def test_slug_must_be_unique(self):
        Collection.objects.create(title="Первая", slug="same")
        c = Collection(title="Вторая", slug="same")
        with self.assertRaises(ValidationError):
            c.full_clean()

    def test_slug_unique_in_database(self):
        Collection.objects.create(title="Первая", slug="same")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Collection.objects.create(title="Вторая", slug="same")


class CollectionItemModelTests(TestCase):
    def setUp(self):
        self.collection = Collection.objects.create(title="Тест", slug="test-1")

    def test_https_and_http_urls_are_accepted(self):
        for url in ["https://ali.click/abc", "http://example.com/x?a=1&b=2"]:
            with self.subTest(url=url):
                item = CollectionItem(collection=self.collection, title="Товар", url=url)
                item.full_clean()

    def test_dangerous_urls_are_rejected(self):
        for url in ["javascript:alert(1)", "data:text/html,hi", "ftp://example.com/x", "не ссылка"]:
            with self.subTest(url=url):
                item = CollectionItem(collection=self.collection, title="Товар", url=url)
                with self.assertRaises(ValidationError):
                    item.full_clean()

    def test_items_are_ordered_by_position(self):
        CollectionItem.objects.create(collection=self.collection, title="B", url="https://b.example", position=2)
        CollectionItem.objects.create(collection=self.collection, title="A", url="https://a.example", position=1)
        titles = [i.title for i in self.collection.items.all()]
        self.assertEqual(titles, ["A", "B"])

    def test_deleting_collection_deletes_items(self):
        CollectionItem.objects.create(collection=self.collection, title="A", url="https://a.example")
        self.collection.delete()
        self.assertEqual(CollectionItem.objects.count(), 0)

    def test_only_http_and_https_schemes_allowed(self):
        for url in ["ftp://example.com/x", "ftps://example.com/x", "file:///etc/passwd"]:
            with self.subTest(url=url):
                item = CollectionItem(collection=self.collection, title="Товар", url=url)
                with self.assertRaises(ValidationError):
                    item.full_clean()
