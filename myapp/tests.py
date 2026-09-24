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
        self.assertEqual(len(response.data["results"]), 1)

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
        cart = cart_response.data["results"][0]
        self.assertEqual(cart["subtotal"], 300)
        self.assertEqual(cart["total_items"], 3)

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

    def test_product_search_filter_and_pagination(self):
        category = Category.objects.create(name="Storage")
        Product.objects.create(
            category=category,
            name="Fast SSD",
            brand="TestBrand",
            product_type="storage",
            price="250.00",
            stock=4,
        )
        Product.objects.create(
            category=category,
            name="Old HDD",
            brand="OtherBrand",
            product_type="storage",
            price="100.00",
            stock=0,
        )

        response = self.client.get(
            "/api/products/?search=SSD&brand=TestBrand&in_stock=true"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["name"], "Fast SSD")

    def test_pc_build_total_and_compatibility(self):
        category = Category.objects.create(name="PC parts")

        def create_part(name, product_type, price, **fields):
            return Product.objects.create(
                category=category,
                name=name,
                brand="Test",
                product_type=product_type,
                price=price,
                stock=1,
                **fields,
            )

        cpu = create_part("CPU", "cpu", "10.00", socket="AM5")
        gpu = create_part("GPU", "gpu", "20.00", recommended_psu=600)
        motherboard = create_part(
            "Motherboard",
            "motherboard",
            "30.00",
            socket="AM5",
            ram_type="DDR5",
        )
        ram = create_part("RAM", "ram", "40.00", ram_type="DDR5")
        storage = create_part("SSD", "storage", "50.00")
        psu = create_part("PSU", "psu", "60.00", wattage=750)
        case = create_part("Case", "case", "70.00")
        wrong_motherboard = create_part(
            "Wrong motherboard",
            "motherboard",
            "30.00",
            socket="LGA1700",
            ram_type="DDR5",
        )
        data = {
            "name": "My PC",
            "cpu": cpu.id,
            "gpu": gpu.id,
            "motherboard": motherboard.id,
            "ram": ram.id,
            "storage": storage.id,
            "psu": psu.id,
            "case": case.id,
            "total_price": "1.00",
        }
        self.client.force_authenticate(self.user)

        response = self.client.post("/api/pc-builds/", data)
        data["motherboard"] = wrong_motherboard.id
        incompatible_response = self.client.post("/api/pc-builds/", data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["total_price"], "280.00")
        self.assertEqual(
            incompatible_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
