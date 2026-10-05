from django.test import TestCase
from django.urls import reverse

from collections_app.models import Collection, CollectionItem


class PublicCollectionTests(TestCase):
    def setUp(self):
        self.c = Collection.objects.create(title="Кухня", slug="kitchen1")
        for pos, (title, url) in enumerate(
            [("Секретное А", "https://a.example/1"), ("Секретное Б", "https://b.example/2")]
        ):
            CollectionItem.objects.create(collection=self.c, title=title, url=url, position=pos)
        self.url = reverse("public_collection", args=["kitchen1"])

    def test_page_is_public(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Кухня")

    def test_unknown_slug_returns_404(self):
        response = self.client.get(reverse("public_collection", args=["nope"]))
        self.assertEqual(response.status_code, 404)

    def test_variants_are_numbered_in_order(self):
        response = self.client.get(self.url)
        html = response.content.decode()
        self.assertLess(html.index("вариант 1"), html.index("вариант 2"))
        self.assertLess(html.index("https://a.example/1"), html.index("https://b.example/2"))

    def test_item_titles_are_hidden_from_visitors(self):
        response = self.client.get(self.url)
        self.assertNotContains(response, "Секретное А")
        self.assertNotContains(response, "Секретное Б")

    def test_links_open_safely(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'target="_blank"')
        self.assertContains(response, "noopener")
        self.assertContains(response, "sponsored")

    def test_title_is_escaped(self):
        Collection.objects.create(title="<script>alert(1)</script>", slug="xss")
        response = self.client.get(reverse("public_collection", args=["xss"]))
        self.assertNotContains(response, "<script>alert(1)</script>")

    def test_public_path_matches_route(self):
        self.assertEqual(self.c.public_path(), "/r/kitchen1/")
