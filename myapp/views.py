from rest_framework.viewsets import ModelViewSet

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
from .serializers import (
    CartItemSerializer,
    CartSerializer,
    CategorySerializer,
    CompareItemSerializer,
    CustomUserSerializer,
    OrderItemSerializer,
    OrderSerializer,
    PCBuildSerializer,
    ProductSerializer,
    ReviewSerializer,
    WishlistSerializer,
)


class CustomUserViewSet(ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


class WishlistViewSet(ModelViewSet):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer


class CompareItemViewSet(ModelViewSet):
    queryset = CompareItem.objects.all()
    serializer_class = CompareItemSerializer


class CartViewSet(ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer


class CartItemViewSet(ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class OrderItemViewSet(ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer


class PCBuildViewSet(ModelViewSet):
    queryset = PCBuild.objects.all()
    serializer_class = PCBuildSerializer
