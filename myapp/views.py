from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

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
from .permissions import IsAdmin, IsManagerOrAdmin, IsOwnerOrReadOnly
from .serializers import (
    CartItemSerializer,
    CartSerializer,
    CategorySerializer,
    CompareItemSerializer,
    CustomUserSerializer,
    OrderItemSerializer,
    OrderSerializer,
    PCBuildSerializer,
    ProfileSerializer,
    ProductSerializer,
    RegisterSerializer,
    ReviewSerializer,
    WishlistSerializer,
)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except (KeyError, TokenError):
            return Response(
                {"error": "Invalid refresh token"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class RegisterViewSet(ModelViewSet):
    queryset = CustomUser.objects.all().order_by("id")
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class CustomUserViewSet(ModelViewSet):
    queryset = CustomUser.objects.all().order_by("id")
    serializer_class = CustomUserSerializer
    permission_classes = [IsAdmin]


class ProfileViewSet(ModelViewSet):
    queryset = CustomUser.objects.all().order_by("id")
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all().order_by("id")
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        if self.request.method == "DELETE":
            return [IsAdmin()]
        return [IsManagerOrAdmin()]


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all().order_by("id")
    serializer_class = ProductSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name", "description", "brand"]
    ordering_fields = ["name", "price", "stock"]

    def get_queryset(self):
        queryset = Product.objects.all().order_by("id")
        category = self.request.query_params.get("category")
        product_type = self.request.query_params.get("product_type")
        brand = self.request.query_params.get("brand")
        min_price = self.request.query_params.get("min_price")
        max_price = self.request.query_params.get("max_price")
        in_stock = self.request.query_params.get("in_stock")

        if category:
            queryset = queryset.filter(category_id=category)
        if product_type:
            queryset = queryset.filter(product_type=product_type)
        if brand:
            queryset = queryset.filter(brand__iexact=brand)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if in_stock == "true":
            queryset = queryset.filter(stock__gt=0)

        return queryset

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        if self.request.method == "DELETE":
            return [IsAdmin()]
        return [IsManagerOrAdmin()]


class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.all().order_by("id")
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated(), IsOwnerOrReadOnly()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WishlistViewSet(ModelViewSet):
    queryset = Wishlist.objects.all().order_by("id")
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Wishlist.objects.none()
        return Wishlist.objects.filter(user=self.request.user).order_by("id")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CompareItemViewSet(ModelViewSet):
    queryset = CompareItem.objects.all().order_by("id")
    serializer_class = CompareItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return CompareItem.objects.none()
        return CompareItem.objects.filter(user=self.request.user).order_by("id")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CartViewSet(ModelViewSet):
    queryset = Cart.objects.all().order_by("id")
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Cart.objects.none()
        return Cart.objects.filter(user=self.request.user).order_by("id")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CartItemViewSet(ModelViewSet):
    queryset = CartItem.objects.all().order_by("id")
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return CartItem.objects.none()
        return CartItem.objects.filter(cart__user=self.request.user).order_by("id")

    def perform_create(self, serializer):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        product = serializer.validated_data["product"]
        quantity = serializer.validated_data.get("quantity", 1)
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={"quantity": quantity},
        )

        if not created:
            new_quantity = item.quantity + quantity
            if new_quantity > product.stock:
                raise ValidationError("Not enough product in stock")
            item.quantity = new_quantity
            item.save()

        serializer.instance = item

    def clear(self, request):
        self.get_queryset().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all().order_by("id")
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Order.objects.none()
        return Order.objects.filter(user=self.request.user).order_by("id")

    def perform_create(self, serializer):
        with transaction.atomic():
            cart = Cart.objects.filter(user=self.request.user).first()
            if not cart or not cart.cartitem_set.exists():
                raise ValidationError("Cart is empty")

            cart_items = cart.cartitem_set.select_related("product")
            total = 0

            for item in cart_items:
                if item.quantity > item.product.stock:
                    raise ValidationError(
                        f"Not enough {item.product.name} in stock"
                    )
                total += item.product.price * item.quantity

            order = serializer.save(user=self.request.user, total=total)

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    price=item.product.price,
                    quantity=item.quantity,
                )
                item.product.stock -= item.quantity
                item.product.save()

            cart.cartitem_set.all().delete()


class OrderItemViewSet(ModelViewSet):
    queryset = OrderItem.objects.all().order_by("id")
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return OrderItem.objects.none()
        return OrderItem.objects.filter(order__user=self.request.user).order_by("id")

class PCBuildViewSet(ModelViewSet):
    queryset = PCBuild.objects.all().order_by("id")
    serializer_class = PCBuildSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return PCBuild.objects.none()
        return PCBuild.objects.filter(user=self.request.user).order_by("id")

    def perform_create(self, serializer):
        fields = ("cpu", "gpu", "motherboard", "ram", "storage", "psu", "case")
        total_price = sum(
            serializer.validated_data[field].price for field in fields
        )
        serializer.save(user=self.request.user, total_price=total_price)

    def perform_update(self, serializer):
        fields = ("cpu", "gpu", "motherboard", "ram", "storage", "psu", "case")
        total_price = sum(
            serializer.validated_data.get(field, getattr(serializer.instance, field)).price
            for field in fields
        )
        serializer.save(total_price=total_price)
