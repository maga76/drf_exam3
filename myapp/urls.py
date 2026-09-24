from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    CartItemViewSet,
    CartViewSet,
    CategoryViewSet,
    CompareItemViewSet,
    CustomUserViewSet,
    OrderItemViewSet,
    OrderViewSet,
    PCBuildViewSet,
    ProductViewSet,
    RegisterViewSet,
    ReviewViewSet,
    WishlistViewSet,
)


urlpatterns = [
    path("register/", RegisterViewSet.as_view({"post": "create"})),
    path("login/", TokenObtainPairView.as_view()),
    path("token/refresh/", TokenRefreshView.as_view()),
    path("users/", CustomUserViewSet.as_view({"get": "list", "post": "create"})),
    path("users/<int:pk>/", CustomUserViewSet.as_view({"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"})),
    path("categories/", CategoryViewSet.as_view({"get": "list", "post": "create"})),
    path("categories/<int:pk>/", CategoryViewSet.as_view({"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"})),
    path("products/", ProductViewSet.as_view({"get": "list", "post": "create"})),
    path("products/<int:pk>/", ProductViewSet.as_view({"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"})),
    path("reviews/", ReviewViewSet.as_view({"get": "list", "post": "create"})),
    path("reviews/<int:pk>/", ReviewViewSet.as_view({"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"})),
    path("wishlist/", WishlistViewSet.as_view({"get": "list", "post": "create"})),
    path("wishlist/<int:pk>/", WishlistViewSet.as_view({"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"})),
    path("compare/", CompareItemViewSet.as_view({"get": "list", "post": "create"})),
    path("compare/<int:pk>/", CompareItemViewSet.as_view({"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"})),
    path("carts/", CartViewSet.as_view({"get": "list", "post": "create"})),
    path("carts/<int:pk>/", CartViewSet.as_view({"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"})),
    path("cart-items/", CartItemViewSet.as_view({"get": "list", "post": "create"})),
    path("cart-items/<int:pk>/", CartItemViewSet.as_view({"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"})),
    path("orders/", OrderViewSet.as_view({"get": "list", "post": "create"})),
    path("orders/<int:pk>/", OrderViewSet.as_view({"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"})),
    path("order-items/", OrderItemViewSet.as_view({"get": "list", "post": "create"})),
    path("order-items/<int:pk>/", OrderItemViewSet.as_view({"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"})),
    path("pc-builds/", PCBuildViewSet.as_view({"get": "list", "post": "create"})),
    path("pc-builds/<int:pk>/", PCBuildViewSet.as_view({"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"})),
]
