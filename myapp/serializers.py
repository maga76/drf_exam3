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
    class Meta:
        model = Order
        fields = "__all__"
        read_only_fields = ("user",)


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = "__all__"


class PCBuildSerializer(serializers.ModelSerializer):
    class Meta:
        model = PCBuild
        fields = "__all__"
        read_only_fields = ("user",)
