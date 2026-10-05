from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from collections_app.models import Collection, CollectionItem

PASSWORD = "correct-horse-battery"


def formset_data(rows, initial=0, prefix="items"):
    data = {
        f"{prefix}-TOTAL_FORMS": len(rows),
        f"{prefix}-INITIAL_FORMS": initial,
        f"{prefix}-MIN_NUM_FORMS": 0,
        f"{prefix}-MAX_NUM_FORMS": 1000,
    }
    for i, row in enumerate(rows):
        for key, value in row.items():
            data[f"{prefix}-{i}-{key}"] = value
    return data


class ManageBase(TestCase):
    def setUp(self):
        get_user_model().objects.create_user(username="owner", password=PASSWORD)
        self.client.login(username="owner", password=PASSWORD)


class AccessTests(TestCase):
    def test_all_manage_pages_require_login(self):
        c = Collection.objects.create(title="T", slug="t")
        urls = [
            reverse("manage:collection_list"),
            reverse("manage:collection_create"),
            reverse("manage:collection_edit", args=[c.pk]),
            reverse("manage:collection_delete", args=[c.pk]),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertIn("/manage/login/", response["Location"])


class CreateTests(ManageBase):
    def post_create(self, slug="kitchen1", rows=None):
        if rows is None:
            rows = [
                {"title": "A", "url": "https://a.example/1"},
                {"title": "B", "url": "https://b.example/2"},
            ]
        data = {"title": "Кухня", "slug": slug, **formset_data(rows)}
        return self.client.post(reverse("manage:collection_create"), data)

    def test_create_saves_items_in_row_order(self):
        response = self.post_create()
        c = Collection.objects.get(slug="kitchen1")
        self.assertRedirects(response, reverse("manage:collection_edit", args=[c.pk]))
        items = list(c.items.all())
        self.assertEqual([i.title for i in items], ["A", "B"])
        self.assertEqual([i.position for i in items], [0, 1])

    def test_create_requires_at_least_one_item(self):
        response = self.post_create(rows=[])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Collection.objects.count(), 0)

    def test_create_rejects_invalid_slug(self):
        response = self.post_create(slug="плохой id")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Collection.objects.count(), 0)

    def test_create_rejects_duplicate_slug(self):
        Collection.objects.create(title="Старая", slug="kitchen1")
        response = self.post_create(slug="kitchen1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Collection.objects.count(), 1)

    def test_create_rejects_non_http_url(self):
        rows = [{"title": "A", "url": "javascript:alert(1)"}]
        response = self.post_create(rows=rows)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Collection.objects.count(), 0)


class EditTests(ManageBase):
    def setUp(self):
        super().setUp()
        self.c = Collection.objects.create(title="Старое", slug="fixed")
        self.a = CollectionItem.objects.create(collection=self.c, title="A", url="https://a.example", position=0)
        self.b = CollectionItem.objects.create(collection=self.c, title="B", url="https://b.example", position=1)
        self.d = CollectionItem.objects.create(collection=self.c, title="C", url="https://c.example", position=2)

    def row(self, item, **extra):
        base = {"id": item.pk, "collection": self.c.pk, "title": item.title, "url": item.url}
        base.update(extra)
        return base

    def test_edit_updates_deletes_adds_and_keeps_slug(self):
        rows = [
            self.row(self.a, title="A2"),
            self.row(self.b, DELETE="on"),
            self.row(self.d),
            {"title": "D", "url": "https://d.example"},
        ]
        data = {"title": "Новое", "slug": "hacked", **formset_data(rows, initial=3)}
        response = self.client.post(reverse("manage:collection_edit", args=[self.c.pk]), data)
        self.assertEqual(response.status_code, 302)
        self.c.refresh_from_db()
        self.assertEqual(self.c.title, "Новое")
        self.assertEqual(self.c.slug, "fixed")
        items = list(self.c.items.all())
        self.assertEqual([i.title for i in items], ["A2", "C", "D"])
        self.assertEqual([i.position for i in items], [0, 1, 2])

    def test_cannot_delete_all_items(self):
        rows = [self.row(i, DELETE="on") for i in (self.a, self.b, self.d)]
        data = {"title": "Старое", "slug": "fixed", **formset_data(rows, initial=3)}
        response = self.client.post(reverse("manage:collection_edit", args=[self.c.pk]), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.c.items.count(), 3)


class DeleteTests(ManageBase):
    def test_get_shows_confirmation_and_does_not_delete(self):
        c = Collection.objects.create(title="T", slug="t")
        response = self.client.get(reverse("manage:collection_delete", args=[c.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Collection.objects.filter(pk=c.pk).exists())

    def test_post_deletes_collection_and_items(self):
        c = Collection.objects.create(title="T", slug="t")
        CollectionItem.objects.create(collection=c, title="A", url="https://a.example")
        response = self.client.post(reverse("manage:collection_delete", args=[c.pk]))
        self.assertRedirects(response, reverse("manage:collection_list"))
        self.assertEqual(Collection.objects.count(), 0)
        self.assertEqual(CollectionItem.objects.count(), 0)
