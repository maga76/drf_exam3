from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

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


admin.site.register(CustomUser, UserAdmin)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Review)
admin.site.register(Wishlist)
admin.site.register(CompareItem)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(PCBuild)
