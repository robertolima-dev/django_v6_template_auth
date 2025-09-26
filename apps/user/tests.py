from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from .models import UserToken


User = get_user_model()


class AuthApiTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.base = "/api/v1"

    def test_register_returns_access_token_and_user(self):
        payload = {
            "email": "register@example.com",
            "first_name": "Reg",
            "last_name": "User",
            "password": "StrongPass123",
            "phone": "+55 11 99999-0000",
            "gender": "m",
            "date_of_birth": "1990-01-01",
        }
        r = self.client.post(f"{self.base}/auth/register/", payload, format="json")
        self.assertEqual(r.status_code, status.HTTP_201_CREATED, r.content)
        self.assertIn("user", r.data)
        self.assertIn("token", r.data)
        self.assertIn("expired_at", r.data)
        self.assertEqual(r.data["user"]["email"], payload["email"])
        self.assertIsInstance(r.data["expired_at"], int)

    def test_login_returns_access_token_and_user(self):
        user = User.objects.create_user(
            username="login_user_1",
            email="login@example.com",
            password="StrongPass123",
        )
        r = self.client.post(
            f"{self.base}/auth/login/",
            {"email": "login@example.com", "password": "StrongPass123"},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK, r.content)
        self.assertIn("token", r.data)
        self.assertIn("expired_at", r.data)
        self.assertEqual(r.data["user"]["email"], user.email)

    def test_forgot_password_returns_token_when_user_exists(self):
        user = User.objects.create_user(
            username="forgot_user_1",
            email="forgot@example.com",
            password="StrongPass123",
        )
        r = self.client.post(
            f"{self.base}/auth/forgot_password/",
            {"email": "forgot@example.com"},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK, r.content)
        self.assertTrue(r.data["sent"])  # always true
        self.assertIn("token", r.data)

    def test_forgot_password_silently_ok_when_user_not_exists(self):
        r = self.client.post(
            f"{self.base}/auth/forgot_password/",
            {"email": "nope@example.com"},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK, r.content)
        self.assertTrue(r.data["sent"])  # token may not be present

    def test_reset_password_with_token(self):
        user = User.objects.create_user(
            username="reset_user_1",
            email="reset@example.com",
            password="OldPass123",
        )
        t = UserToken.objects.create(
            token="reset-token-123",
            user=user,
            token_type="change_password",
            expired_at=timezone.now() + timezone.timedelta(hours=1),
        )
        r = self.client.post(
            f"{self.base}/auth/reset_password/",
            {"token": t.token, "password": "NewPass123"},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK, r.content)
        # login with new password works
        r2 = self.client.post(
            f"{self.base}/auth/login/",
            {"email": user.email, "password": "NewPass123"},
            format="json",
        )
        self.assertEqual(r2.status_code, status.HTTP_200_OK, r2.content)

    def test_confirm_email_marks_user_and_returns_access(self):
        user = User.objects.create_user(
            username="confirm_user_1",
            email="confirm@example.com",
            password="Pass12345",
        )
        t = UserToken.objects.create(
            token="confirm-token-123",
            user=user,
            token_type="confirm_email",
            expired_at=timezone.now() + timezone.timedelta(days=1),
        )
        r = self.client.post(
            f"{self.base}/auth/confirm_email/",
            {"token": t.token},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK, r.content)
        user.refresh_from_db()
        self.assertTrue(user.confirm_email)

    def test_users_me_echoes_same_token(self):
        user = User.objects.create_user(
            username="me_user_1",
            email="me@example.com",
            password="Pass12345",
        )
        # get access via login
        r = self.client.post(
            f"{self.base}/auth/login/",
            {"email": user.email, "password": "Pass12345"},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        token = r.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        r2 = self.client.get(f"{self.base}/users/me/")
        self.assertEqual(r2.status_code, status.HTTP_200_OK, r2.content)
        self.assertEqual(r2.data["token"], token)
        self.assertIsInstance(r2.data["expired_at"], int)
