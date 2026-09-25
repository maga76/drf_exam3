from rest_framework import status
from rest_framework.test import APITestCase

from .models import Cart, CartItem, Category, CustomUser, Order, OrderItem, Product


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

    def test_manager_can_change_order_status(self):
        order = Order.objects.create(
            user=self.user,
            first_name="Test",
            last_name="User",
            phone="900000000",
            city="Dushanbe",
            address="Test address",
        )
        self.client.force_authenticate(self.user)
        user_response = self.client.patch(
            f"/api/orders/{order.id}/status/",
            {"status": "confirmed"},
        )

        self.client.force_authenticate(self.manager)
        manager_response = self.client.patch(
            f"/api/orders/{order.id}/status/",
            {"status": "confirmed"},
        )
        order_list = self.client.get("/api/orders/")
        order.refresh_from_db()

        self.assertEqual(user_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(manager_response.status_code, status.HTTP_200_OK)
        self.assertEqual(order.status, "confirmed")
        self.assertEqual(order_list.data["count"], 1)

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
        compatibility_response = self.client.post(
            "/api/compatibility/check/",
            {
                "cpu": cpu.id,
                "gpu": gpu.id,
                "motherboard": motherboard.id,
                "ram": ram.id,
                "storage": storage.id,
                "psu": psu.id,
                "case": case.id,
            },
        )
        data["motherboard"] = wrong_motherboard.id
        incompatible_response = self.client.post("/api/pc-builds/", data)
        incompatible_check = self.client.post(
            "/api/compatibility/check/",
            {
                "cpu": cpu.id,
                "gpu": gpu.id,
                "motherboard": wrong_motherboard.id,
                "ram": ram.id,
                "storage": storage.id,
                "psu": psu.id,
                "case": case.id,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["total_price"], "280.00")
        self.assertTrue(compatibility_response.data["compatible"])
        self.assertEqual(
            incompatible_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertFalse(incompatible_check.data["compatible"])

    def test_laptop_and_pc_recommendations(self):
        category = Category.objects.create(name="Recommendation")
        Product.objects.create(
            category=category,
            name="Recommended laptop",
            brand="Test",
            product_type="laptop",
            price="900.00",
            stock=2,
            screen_score=9,
            battery_score=8,
            performance_score=10,
            gaming_score=7,
        )

        laptop_response = self.client.post(
            "/api/recommendations/laptops/",
            {
                "budget": "1000.00",
                "good_screen": True,
                "long_battery": True,
                "programming": True,
            },
        )

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

        create_part("CPU", "cpu", "10.00", socket="AM5")
        create_part("GPU", "gpu", "20.00", recommended_psu=600)
        create_part(
            "Motherboard",
            "motherboard",
            "30.00",
            socket="AM5",
            ram_type="DDR5",
        )
        create_part("RAM", "ram", "40.00", ram_type="DDR5")
        create_part("SSD", "storage", "50.00")
        create_part("PSU", "psu", "60.00", wattage=750)
        create_part("Case", "case", "70.00")

        pc_response = self.client.post(
            "/api/recommendations/pc/",
            {"budget": "300.00", "gaming": True},
        )

        self.assertEqual(laptop_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            laptop_response.data["results"][0]["product"]["name"],
            "Recommended laptop",
        )
        self.assertEqual(laptop_response.data["results"][0]["score"], 27)
        self.assertEqual(pc_response.status_code, status.HTTP_200_OK)
        self.assertTrue(pc_response.data["success"])
        self.assertEqual(pc_response.data["total_price"], 280)

    def test_reviews_wishlist_and_compare_validation(self):
        category = Category.objects.create(name="Validation")
        products = [
            Product.objects.create(
                category=category,
                name=f"Product {number}",
                brand="Test",
                product_type="other",
                price="10.00",
                stock=1,
            )
            for number in range(5)
        ]
        self.client.force_authenticate(self.user)

        bad_review = self.client.post(
            "/api/reviews/",
            {"product": products[0].id, "rating": 6, "text": "Bad rating"},
        )
        review = self.client.post(
            "/api/reviews/",
            {"product": products[0].id, "rating": 5, "text": "Good"},
        )
        duplicate_review = self.client.post(
            "/api/reviews/",
            {"product": products[0].id, "rating": 4, "text": "Again"},
        )
        filtered_reviews = self.client.get(
            f"/api/reviews/?product={products[0].id}"
        )
        product_detail = self.client.get(f"/api/products/{products[0].id}/")
        wishlist = self.client.post(
            "/api/wishlist/",
            {"product": products[0].id},
        )
        duplicate_wishlist = self.client.post(
            "/api/wishlist/",
            {"product": products[0].id},
        )
        compare_responses = [
            self.client.post("/api/compare/", {"product": product.id})
            for product in products
        ]

        self.assertEqual(bad_review.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(review.status_code, status.HTTP_201_CREATED)
        self.assertEqual(duplicate_review.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(filtered_reviews.data["count"], 1)
        self.assertEqual(product_detail.data["average_rating"], 5.0)
        self.assertEqual(product_detail.data["review_count"], 1)
        self.assertEqual(wishlist.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            duplicate_wishlist.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertTrue(
            all(response.status_code == status.HTTP_201_CREATED for response in compare_responses[:4])
        )
        self.assertEqual(
            compare_responses[4].status_code,
            status.HTTP_400_BAD_REQUEST,
        )
