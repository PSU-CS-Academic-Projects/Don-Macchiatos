from django.contrib import admin
from .models import Category, MenuItem, Order, OrderItem, ContactMessage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    # prepopulated_fields auto-fills 'slug' as you type the name


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_available']
    list_filter = ['category', 'is_available']
    list_editable = ['price', 'is_available']
    # list_editable lets you edit directly in the list view!
    search_fields = ['name', 'description']


class OrderItemInline(admin.TabularInline):
    """Shows order items inside the Order detail page."""
    model = OrderItem
    extra = 0  # Don't show empty extra rows
    readonly_fields = ['price_at_order']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['pk', 'customer_name', 'contact_number',
                    'delivery_method', 'status', 'total_price', 'created_at']
    list_filter = ['status', 'delivery_method']
    list_editable = ['status']
    inlines = [OrderItemInline]  # Show order items on the same page
    readonly_fields = ['created_at', 'session_key']


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'submitted_at', 'is_read']
    list_editable = ['is_read']
    readonly_fields = ['submitted_at']