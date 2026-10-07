from django.test import TestCase
from django.urls import reverse

from collections_app.models import Collection, CollectionItem


class PublicCollectionTests(TestCase):
    def setUp(self):
        self.c = Collection.objects.create(title="Кухня", slug="kitchen1")
        CollectionItem.objects.create(
            collection=self.c, title="Терка", url="https://a.example/1", position=0
        )
        CollectionItem.objects.create(
            collection=self.c, title="", url="https://b.example/2", position=1
        )
        self.url = reverse("public_collection", args=["kitchen1"])

    def test_page_is_public(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Кухня")

    def test_unknown_slug_returns_404(self):
        response = self.client.get(reverse("public_collection", args=["nope"]))
        self.assertEqual(response.status_code, 404)

    def test_named_item_shows_its_title(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Терка")
        self.assertNotContains(response, "вариант 1")

    def test_unnamed_item_falls_back_to_variant_number(self):
        response = self.client.get(self.url)
        self.assertContains(response, "вариант 2")

    def test_items_keep_their_order(self):
        html = self.client.get(self.url).content.decode()
        self.assertLess(html.index("Терка"), html.index("вариант 2"))
        self.assertLess(html.index("https://a.example/1"), html.index("https://b.example/2"))

    def test_links_open_safely(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'target="_blank"')
        self.assertContains(response, "noopener")
        self.assertContains(response, "sponsored")

    def test_collection_title_is_escaped(self):
        Collection.objects.create(title="<script>alert(1)</script>", slug="xss")
        response = self.client.get(reverse("public_collection", args=["xss"]))
        self.assertNotContains(response, "<script>alert(1)</script>")

    def test_item_title_is_escaped(self):
        CollectionItem.objects.create(
            collection=self.c, title="<b>x</b>", url="https://c.example/3", position=2
        )
        response = self.client.get(self.url)
        self.assertNotContains(response, "<b>x</b>")

    def test_public_path_matches_route(self):
        self.assertEqual(self.c.public_path(), "/r/kitchen1/")
