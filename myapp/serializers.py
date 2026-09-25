from rest_framework import serializers

from .models import (
    Cart,
    CartItem,
    Category,
    CompareItem,
    CustomUser,
    Order,
    OrderItem,
    PCBuild,
    Product,
    Review,
    Wishlist,
)


BUILD_FIELDS = ("cpu", "gpu", "motherboard", "ram", "storage", "psu", "case")


def check_compatibility(parts):
    errors = []

    for field in BUILD_FIELDS:
        part = parts.get(field)
        if part and part.product_type != field:
            errors.append(f"{field} has the wrong product type")

    cpu = parts.get("cpu")
    motherboard = parts.get("motherboard")
    ram = parts.get("ram")
    gpu = parts.get("gpu")
    psu = parts.get("psu")

    if cpu and motherboard and cpu.socket != motherboard.socket:
        errors.append("CPU socket does not match motherboard")
    if ram and motherboard and ram.ram_type != motherboard.ram_type:
        errors.append("RAM type does not match motherboard")
    if gpu and psu and psu.wattage < gpu.recommended_psu:
        errors.append("PSU is too weak for GPU")

    return errors


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("id", "username", "email", "phone", "role", "avatar")


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("id", "username", "email", "phone", "role", "avatar")
        read_only_fields = ("id", "role")


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ("username", "email", "password", "phone")

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"
        read_only_fields = ("user",)


class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = "__all__"
        read_only_fields = ("user",)


class CompareItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompareItem
        fields = "__all__"
        read_only_fields = ("user",)


class CartSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ("id", "user", "items", "subtotal", "total_items")
        read_only_fields = ("user",)

    def get_items(self, obj):
        items = obj.cartitem_set.all()
        return CartItemSerializer(items, many=True).data

    def get_subtotal(self, obj):
        return sum(item.product.price * item.quantity for item in obj.cartitem_set.all())

    def get_total_items(self, obj):
        return sum(item.quantity for item in obj.cartitem_set.all())


class CartItemSerializer(serializers.ModelSerializer):
    item_total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ("id", "cart", "product", "quantity", "item_total")
        read_only_fields = ("cart",)

    def get_item_total(self, obj):
        return obj.product.price * obj.quantity

    def validate(self, data):
        product = data.get("product")
        quantity = data.get("quantity", 1)

        if self.instance:
            product = product or self.instance.product
            quantity = data.get("quantity", self.instance.quantity)

        if quantity < 1:
            raise serializers.ValidationError("Quantity must be at least 1")
        if quantity > product.stock:
            raise serializers.ValidationError("Not enough product in stock")

        return data


class OrderSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            "id",
            "user",
            "status",
            "first_name",
            "last_name",
            "phone",
            "city",
            "address",
            "total",
            "created_at",
            "items",
        )
        read_only_fields = ("user", "status", "total", "created_at")

    def get_items(self, obj):
        items = obj.orderitem_set.all()
        return OrderItemSerializer(items, many=True).data


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = "__all__"


class PCBuildSerializer(serializers.ModelSerializer):
    class Meta:
        model = PCBuild
        fields = "__all__"
        read_only_fields = ("user", "total_price")

    def validate(self, data):
        parts = {}

        for field in BUILD_FIELDS:
            part = data.get(field)
            if self.instance:
                part = part or getattr(self.instance, field)
            parts[field] = part

        errors = check_compatibility(parts)

        if errors:
            raise serializers.ValidationError(errors)

        return data


class CompatibilitySerializer(serializers.Serializer):
    cpu = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    gpu = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    motherboard = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    ram = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    storage = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    psu = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    case = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())


class LaptopRecommendationSerializer(serializers.Serializer):
    budget = serializers.DecimalField(max_digits=10, decimal_places=2)
    good_screen = serializers.BooleanField(default=False)
    long_battery = serializers.BooleanField(default=False)
    gaming = serializers.BooleanField(default=False)
    programming = serializers.BooleanField(default=False)


class PCRecommendationSerializer(serializers.Serializer):
    budget = serializers.DecimalField(max_digits=10, decimal_places=2)
    gaming = serializers.BooleanField(default=False)
    programming = serializers.BooleanField(default=False)
