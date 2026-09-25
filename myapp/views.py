from django.db import transaction
from django.shortcuts import get_object_or_404
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
    BUILD_FIELDS,
    CartItemSerializer,
    CartSerializer,
    CategorySerializer,
    CompatibilitySerializer,
    CompareItemSerializer,
    CustomUserSerializer,
    LaptopRecommendationSerializer,
    OrderItemSerializer,
    OrderSerializer,
    OrderStatusSerializer,
    PCBuildSerializer,
    PCRecommendationSerializer,
    ProfileSerializer,
    ProductSerializer,
    RegisterSerializer,
    ReviewSerializer,
    WishlistSerializer,
    check_compatibility,
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


class CompatibilityView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CompatibilitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        errors = check_compatibility(serializer.validated_data)
        return Response({"compatible": not errors, "errors": errors})


class LaptopRecommendationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LaptopRecommendationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        laptops = Product.objects.filter(
            product_type="laptop",
            stock__gt=0,
            price__lte=data["budget"],
        )
        results = []

        for laptop in laptops:
            score = 0
            reasons = []

            if data["good_screen"]:
                score += laptop.screen_score
                reasons.append("Good screen")
            if data["long_battery"]:
                score += laptop.battery_score
                reasons.append("Long battery life")
            if data["gaming"]:
                score += laptop.gaming_score
                reasons.append("Good for gaming")
            if data["programming"]:
                score += laptop.performance_score
                reasons.append("Good for programming")

            results.append(
                {
                    "product": ProductSerializer(laptop).data,
                    "score": score,
                    "reasons": reasons,
                }
            )

        results.sort(key=lambda item: item["score"], reverse=True)

        if not results:
            return Response(
                {"results": [], "message": "No suitable products found"}
            )

        return Response({"results": results[:5]})


class PCRecommendationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PCRecommendationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        cpu_order = "-performance_score" if data["programming"] else "price"
        gpu_order = "-gaming_score" if data["gaming"] else "price"
        cpus = Product.objects.filter(product_type="cpu", stock__gt=0).order_by(
            cpu_order, "price"
        )
        gpus = Product.objects.filter(product_type="gpu", stock__gt=0).order_by(
            gpu_order, "price"
        )
        storage = Product.objects.filter(
            product_type="storage", stock__gt=0
        ).order_by("price").first()
        case = Product.objects.filter(product_type="case", stock__gt=0).order_by(
            "price"
        ).first()

        if not storage or not case:
            return Response(
                {
                    "success": False,
                    "message": "Could not build a compatible PC within the budget",
                }
            )

        for cpu in cpus:
            motherboard = Product.objects.filter(
                product_type="motherboard",
                socket=cpu.socket,
                stock__gt=0,
            ).order_by("price").first()
            if not motherboard:
                continue

            ram = Product.objects.filter(
                product_type="ram",
                ram_type=motherboard.ram_type,
                stock__gt=0,
            ).order_by("price").first()
            if not ram:
                continue

            for gpu in gpus:
                psu = Product.objects.filter(
                    product_type="psu",
                    wattage__gte=gpu.recommended_psu,
                    stock__gt=0,
                ).order_by("price").first()
                if not psu:
                    continue

                parts = {
                    "cpu": cpu,
                    "gpu": gpu,
                    "motherboard": motherboard,
                    "ram": ram,
                    "storage": storage,
                    "psu": psu,
                    "case": case,
                }
                total_price = sum(part.price for part in parts.values())

                if total_price <= data["budget"]:
                    components = {
                        name: ProductSerializer(part).data
                        for name, part in parts.items()
                    }
                    return Response(
                        {
                            "success": True,
                            "total_price": total_price,
                            "components": components,
                            "compatible": True,
                        }
                    )

        return Response(
            {
                "success": False,
                "message": "Could not build a compatible PC within the budget",
            }
        )


class OrderStatusView(APIView):
    permission_classes = [IsManagerOrAdmin]

    def patch(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        serializer = OrderStatusSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


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

    def get_queryset(self):
        queryset = Review.objects.all().order_by("id")
        product = self.request.query_params.get("product")
        if product:
            queryset = queryset.filter(product_id=product)
        return queryset

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
        if self.request.user.role in ("manager", "admin"):
            return Order.objects.all().order_by("id")
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
        total_price = sum(
            serializer.validated_data[field].price for field in BUILD_FIELDS
        )
        serializer.save(user=self.request.user, total_price=total_price)

    def perform_update(self, serializer):
        total_price = sum(
            serializer.validated_data.get(field, getattr(serializer.instance, field)).price
            for field in BUILD_FIELDS
        )
        serializer.save(total_price=total_price)
