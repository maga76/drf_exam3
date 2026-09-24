from rest_framework import status
from rest_framework.test import APITestCase

from .models import Cart, CartItem, Category, CustomUser, OrderItem, Product


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

    def test_cart_checks_stock_and_calculates_total(self):
        category = Category.objects.create(name="Processors")
        product = Product.objects.create(
            category=category,
            name="Test CPU",
            brand="Test",
            product_type="cpu",
            price="100.00",
            stock=3,
        )
        self.client.force_authenticate(self.user)

        first_response = self.client.post(
            "/api/cart-items/",
            {"product": product.id, "quantity": 2},
        )
        second_response = self.client.post(
            "/api/cart-items/",
            {"product": product.id, "quantity": 1},
        )
        no_stock_response = self.client.post(
            "/api/cart-items/",
            {"product": product.id, "quantity": 1},
        )
        cart_response = self.client.get("/api/carts/")

        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(no_stock_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(CartItem.objects.get().quantity, 3)
        self.assertEqual(cart_response.data[0]["subtotal"], 300)
        self.assertEqual(cart_response.data[0]["total_items"], 3)

        clear_response = self.client.delete("/api/cart/clear/")

        self.assertEqual(clear_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(CartItem.objects.count(), 0)

    def test_order_is_created_from_cart(self):
        category = Category.objects.create(name="Video cards")
        product = Product.objects.create(
            category=category,
            name="Test GPU",
            brand="Test",
            product_type="gpu",
            price="500.00",
            stock=5,
        )
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=product, quantity=2)
        self.client.force_authenticate(self.user)

        response = self.client.post(
            "/api/orders/",
            {
                "first_name": "Test",
                "last_name": "User",
                "phone": "900000000",
                "city": "Dushanbe",
                "address": "Test address",
                "total": "1.00",
                "status": "delivered",
            },
        )
        product.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "pending")
        self.assertEqual(response.data["total"], "1000.00")
        self.assertEqual(product.stock, 3)
        self.assertEqual(CartItem.objects.count(), 0)
        self.assertEqual(OrderItem.objects.count(), 1)
