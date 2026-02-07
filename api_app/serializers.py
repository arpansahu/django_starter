"""
API App Serializers - Django REST Framework Serializers
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Product, Review, Order, OrderItem, UserProfile, APIKey

User = get_user_model()


# =============================================================================
# USER SERIALIZERS
# =============================================================================

class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined', 'is_active']
        read_only_fields = ['id', 'date_joined']


class UserCreateSerializer(serializers.ModelSerializer):
    """User registration serializer"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm']
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match.'})
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """User profile serializer"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'bio', 'avatar_url', 'phone', 'address', 
                  'date_of_birth', 'is_premium', 'created_at', 'updated_at']
        read_only_fields = ['id', 'is_premium', 'created_at', 'updated_at']


# =============================================================================
# PRODUCT SERIALIZERS
# =============================================================================

class ProductListSerializer(serializers.ModelSerializer):
    """Product list serializer (minimal fields)"""
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'category', 'category_display', 
                  'price', 'is_in_stock', 'is_active']


class ProductDetailSerializer(serializers.ModelSerializer):
    """Product detail serializer (all fields)"""
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'description', 'category', 'category_display',
                  'price', 'stock', 'is_in_stock', 'is_active', 'average_rating',
                  'review_count', 'reviews', 'created_at', 'updated_at']
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']
    
    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews:
            return round(sum(r.rating for r in reviews) / len(reviews), 1)
        return None
    
    def get_review_count(self, obj):
        return obj.reviews.count()
    
    def get_reviews(self, obj):
        reviews = obj.reviews.filter(is_verified=True)[:5]
        return ReviewSerializer(reviews, many=True).data


class ProductCreateSerializer(serializers.ModelSerializer):
    """Product create/update serializer"""
    
    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'price', 'stock', 'is_active']
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError('Price must be greater than zero.')
        return value
    
    def create(self, validated_data):
        from django.utils.text import slugify
        import uuid
        validated_data['slug'] = f"{slugify(validated_data['name'])}-{uuid.uuid4().hex[:8]}"
        return super().create(validated_data)


# =============================================================================
# REVIEW SERIALIZERS
# =============================================================================

class ReviewSerializer(serializers.ModelSerializer):
    """Review serializer"""
    user = UserSerializer(read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'product', 'product_name', 'user', 'rating', 'title', 
                  'content', 'is_verified', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'is_verified', 'created_at', 'updated_at']
    
    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError('Rating must be between 1 and 5.')
        return value
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


# =============================================================================
# ORDER SERIALIZERS
# =============================================================================

class OrderItemSerializer(serializers.ModelSerializer):
    """Order item serializer"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price', 'subtotal']
        read_only_fields = ['id', 'price']


class OrderSerializer(serializers.ModelSerializer):
    """Order serializer"""
    items = OrderItemSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'status_display', 'total_amount',
                  'shipping_address', 'notes', 'items', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'total_amount', 'created_at', 'updated_at']


class OrderCreateSerializer(serializers.Serializer):
    """Order create serializer"""
    shipping_address = serializers.CharField()
    notes = serializers.CharField(required=False, allow_blank=True)
    items = serializers.ListField(
        child=serializers.DictField(),
        min_length=1
    )
    
    def validate_items(self, value):
        for item in value:
            if 'product_id' not in item or 'quantity' not in item:
                raise serializers.ValidationError(
                    'Each item must have product_id and quantity.'
                )
            if item['quantity'] < 1:
                raise serializers.ValidationError('Quantity must be at least 1.')
            
            # Check product exists and has stock
            try:
                product = Product.objects.get(pk=item['product_id'], is_active=True)
                if product.stock < item['quantity']:
                    raise serializers.ValidationError(
                        f'Not enough stock for {product.name}.'
                    )
            except Product.DoesNotExist:
                raise serializers.ValidationError(
                    f'Product with id {item["product_id"]} not found.'
                )
        return value
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context['request'].user
        
        order = Order.objects.create(
            user=user,
            shipping_address=validated_data['shipping_address'],
            notes=validated_data.get('notes', '')
        )
        
        for item_data in items_data:
            product = Product.objects.get(pk=item_data['product_id'])
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item_data['quantity'],
                price=product.price
            )
            # Reduce stock
            product.stock -= item_data['quantity']
            product.save(update_fields=['stock'])
        
        order.calculate_total()
        return order


# =============================================================================
# API KEY SERIALIZERS
# =============================================================================

class APIKeySerializer(serializers.ModelSerializer):
    """API Key serializer"""
    
    class Meta:
        model = APIKey
        fields = ['id', 'name', 'key', 'is_active', 'rate_limit', 
                  'last_used', 'created_at', 'expires_at']
        read_only_fields = ['id', 'key', 'last_used', 'created_at']


class APIKeyCreateSerializer(serializers.ModelSerializer):
    """API Key create serializer"""
    
    class Meta:
        model = APIKey
        fields = ['name', 'rate_limit', 'expires_at']
    
    def create(self, validated_data):
        import secrets
        validated_data['user'] = self.context['request'].user
        validated_data['key'] = secrets.token_hex(32)
        return super().create(validated_data)
