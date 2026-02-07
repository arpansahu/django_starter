from django.contrib import admin
from .models import Product, Review, Order, OrderItem, UserProfile, APIKey


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['price', 'stock', 'is_active']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'is_verified', 'created_at']
    list_filter = ['rating', 'is_verified', 'created_at']
    search_fields = ['title', 'content', 'user__username', 'product__name']
    raw_id_fields = ['product', 'user']
    
    actions = ['verify_reviews']
    
    def verify_reviews(self, request, queryset):
        queryset.update(is_verified=True)
    verify_reviews.short_description = 'Mark selected reviews as verified'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['subtotal']
    raw_id_fields = ['product']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'user__email', 'shipping_address']
    raw_id_fields = ['user']
    readonly_fields = ['total_amount', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    
    actions = ['mark_shipped', 'mark_delivered']
    
    def mark_shipped(self, request, queryset):
        queryset.update(status=Order.Status.SHIPPED)
    mark_shipped.short_description = 'Mark selected orders as shipped'
    
    def mark_delivered(self, request, queryset):
        queryset.update(status=Order.Status.DELIVERED)
    mark_delivered.short_description = 'Mark selected orders as delivered'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'is_premium', 'created_at']
    list_filter = ['is_premium', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone']
    raw_id_fields = ['user']


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'is_active', 'rate_limit', 'last_used', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'user__username', 'key']
    raw_id_fields = ['user']
    readonly_fields = ['key', 'last_used', 'created_at']
