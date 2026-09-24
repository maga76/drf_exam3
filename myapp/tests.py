from rest_framework import status
from rest_framework.test import APITestCase

from .models import Cart, Category, CustomUser


class ApiTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="user",
            password="TestPass123!",
        )
        self.manager = CustomUser.objects.create_user(
            username="manager",
            password="TestPass123!",
            role="manager",
        )
        self.admin = CustomUser.objects.create_user(
            username="admin",
            password="TestPass123!",
            role="admin",
        )

    def test_register_and_login(self):
        register_response = self.client.post(
            "/api/register/",
            {
                "username": "new_user",
                "email": "new@example.com",
                "password": "TestPass123!",
            },
        )
        login_response = self.client.post(
            "/api/login/",
            {"username": "new_user", "password": "TestPass123!"},
        )

        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", login_response.data)
        self.assertIn("refresh", login_response.data)

    def test_products_are_public(self):
        response = self.client.get("/api/products/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_update_profile_but_not_role(self):
        self.client.force_authenticate(self.user)

        response = self.client.patch(
            "/api/profile/",
            {"phone": "900000000", "role": "admin"},
        )
        self.user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.phone, "900000000")
        self.assertEqual(self.user.role, "user")

    def test_manager_can_create_category_but_cannot_delete_it(self):
        self.client.force_authenticate(self.manager)
        create_response = self.client.post(
            "/api/categories/",
            {"name": "Components"},
        )
        delete_response = self.client.delete(
            f"/api/categories/{create_response.data['id']}/"
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(delete_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_delete_category(self):
        category = Category.objects.create(name="Laptops")
        self.client.force_authenticate(self.admin)

        response = self.client.delete(f"/api/categories/{category.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_sees_only_own_cart(self):
        Cart.objects.create(user=self.user)
        Cart.objects.create(user=self.manager)
        self.client.force_authenticate(self.user)

        response = self.client.get("/api/carts/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
