from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ("user", "User"),
        ("manager", "Manager"),
        ("admin", "Admin"),
    )

    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="user")
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="categories/", blank=True, null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    TYPE_CHOICES = (
        ("laptop", "Laptop"),
        ("desktop", "Desktop PC"),
        ("cpu", "CPU"),
        ("gpu", "GPU"),
        ("motherboard", "Motherboard"),
        ("ram", "RAM"),
        ("storage", "Storage"),
        ("psu", "PSU"),
        ("case", "Case"),
        ("cooling", "Cooling"),
        ("monitor", "Monitor"),
        ("other", "Other"),
    )

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=100)
    product_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    image = models.ImageField(upload_to="products/", blank=True, null=True)

    cpu = models.CharField(max_length=100, blank=True)
    gpu = models.CharField(max_length=100, blank=True)
    socket = models.CharField(max_length=50, blank=True)
    ram_type = models.CharField(max_length=50, blank=True)
    ram_gb = models.IntegerField(default=0)
    storage_gb = models.IntegerField(default=0)
    wattage = models.IntegerField(default=0)
    recommended_psu = models.IntegerField(default=0)
    screen_score = models.IntegerField(default=0)
    battery_score = models.IntegerField(default=0)
    performance_score = models.IntegerField(default=0)
    gaming_score = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Review(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField()
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.name


class Wishlist(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return self.product.name


class CompareItem(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return self.product.name


class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return self.product.name


class Order(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.first_name


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return self.product.name


class PCBuild(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    cpu = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="build_cpu")
    gpu = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="build_gpu")
    motherboard = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="build_motherboard")
    ram = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="build_ram")
    storage = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="build_storage")
    psu = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="build_psu")
    case = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="build_case")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.name
