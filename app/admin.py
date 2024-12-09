from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from app.models import User, Menu, Basket, Order


@admin.register(User)
class UserAdmin(UserAdmin):
    ordering = ('email',)
    list_display = ('email', 'first_name', 'last_name', 'phone_number', 'role', 'latitude', 'longitude')
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "phone_number", "role", 'latitude', 'longitude')}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )


@admin.register(Menu)
class MenuAdmin(ModelAdmin):
    list_display = ["name", "price", "is_available", 'created_at', 'updated_at']
    search_fields = ['name', ]
    search_help_text = "Nom bo'yicha qidirish"


@admin.register(Basket)
class Basket(ModelAdmin):
    list_display = ['food', 'quantity', 'price', 'user']
    search_fields = ['user']
    search_help_text = 'User boyicha qidiqish'


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ['user', 'status', 'price', 'quantity']
    search_fields = ['status']
    search_help_text = 'Status boyicha qidirish'
