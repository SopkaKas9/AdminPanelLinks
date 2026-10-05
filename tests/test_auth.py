from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class ManageAuthTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="owner", password="correct-horse-battery"
        )

    def test_manage_requires_login(self):
        response = self.client.get(reverse("manage:collection_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/manage/login/", response["Location"])

    def test_login_with_wrong_password_fails(self):
        response = self.client.post(
            reverse("manage:login"),
            {"username": "owner", "password": "wrong"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_login_with_correct_password_works(self):
        response = self.client.post(
            reverse("manage:login"),
            {"username": "owner", "password": "correct-horse-battery"},
        )
        self.assertRedirects(response, reverse("manage:collection_list"))

    def test_logged_in_user_sees_list(self):
        self.client.login(username="owner", password="correct-horse-battery")
        response = self.client.get(reverse("manage:collection_list"))
        self.assertEqual(response.status_code, 200)

    def test_logout_requires_post(self):
        self.client.login(username="owner", password="correct-horse-battery")
        response = self.client.get(reverse("manage:logout"))
        self.assertEqual(response.status_code, 405)

    def test_logout_works_with_post(self):
        self.client.login(username="owner", password="correct-horse-battery")
        response = self.client.post(reverse("manage:logout"))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn("_auth_user_id", self.client.session)
