"""
API App Views - Complete Django REST Framework Views

This module demonstrates ALL DRF view types:
- ViewSet / ModelViewSet
- GenericAPIView
- APIView
- Mixins
- Custom actions
"""
from rest_framework import viewsets, generics, views, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticated, IsAdminUser, AllowAny, IsAuthenticatedOrReadOnly
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, Q
from drf_spectacular.utils import (
    extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
)
from drf_spectacular.types import OpenApiTypes

from .models import Product, Review, Order, OrderItem, UserProfile, APIKey
from .serializers import (
    UserSerializer, UserCreateSerializer, UserProfileSerializer,
    ProductListSerializer, ProductDetailSerializer, ProductCreateSerializer,
    ReviewSerializer, OrderSerializer, OrderCreateSerializer,
    OrderItemSerializer, APIKeySerializer, APIKeyCreateSerializer
)

User = get_user_model()


# =============================================================================
# PAGINATION
# =============================================================================

class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination class"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class LargeResultsSetPagination(PageNumberPagination):
    """Large pagination for bulk endpoints"""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 500


# =============================================================================
# THROTTLING
# =============================================================================

class BurstRateThrottle(UserRateThrottle):
    rate = '60/min'


class SustainedRateThrottle(UserRateThrottle):
    rate = '1000/day'


# =============================================================================
# MODEL VIEWSETS - Full CRUD operations
# =============================================================================

@extend_schema_view(
    list=extend_schema(
        summary='List all products',
        description='Retrieve a paginated list of all active products.',
        parameters=[
            OpenApiParameter('category', OpenApiTypes.STR, description='Filter by category'),
            OpenApiParameter('min_price', OpenApiTypes.FLOAT, description='Minimum price'),
            OpenApiParameter('max_price', OpenApiTypes.FLOAT, description='Maximum price'),
            OpenApiParameter('in_stock', OpenApiTypes.BOOL, description='Only in-stock products'),
        ],
        tags=['Products']
    ),
    retrieve=extend_schema(
        summary='Get product details',
        description='Retrieve detailed information about a specific product.',
        tags=['Products']
    ),
    create=extend_schema(
        summary='Create a product',
        description='Create a new product (admin only).',
        tags=['Products']
    ),
    update=extend_schema(
        summary='Update a product',
        description='Update all fields of a product (admin only).',
        tags=['Products']
    ),
    partial_update=extend_schema(
        summary='Partial update product',
        description='Update specific fields of a product (admin only).',
        tags=['Products']
    ),
    destroy=extend_schema(
        summary='Delete a product',
        description='Delete a product (admin only).',
        tags=['Products']
    ),
)
class ProductViewSet(viewsets.ModelViewSet):
    """
    Complete CRUD operations for Products.
    
    Demonstrates:
    - ModelViewSet with all CRUD operations
    - Different serializers for list/detail
    - Custom filtering
    - Search and ordering
    - Custom actions
    - Permission handling
    """
    queryset = Product.objects.filter(is_active=True)
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProductCreateSerializer
        return ProductDetailSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [AllowAny()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Custom filtering
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        in_stock = self.request.query_params.get('in_stock')
        
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if in_stock and in_stock.lower() == 'true':
            queryset = queryset.filter(stock__gt=0)
        
        return queryset
    
    @extend_schema(
        summary='Get featured products',
        description='Returns a list of featured products (top rated).',
        tags=['Products']
    )
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured products (highest rated)"""
        featured = self.get_queryset().annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        ).filter(
            review_count__gte=1
        ).order_by('-avg_rating')[:10]
        
        serializer = ProductListSerializer(featured, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary='Get products by category',
        description='Returns products for a specific category.',
        tags=['Products']
    )
    @action(detail=False, methods=['get'], url_path='category/(?P<category>[^/.]+)')
    def by_category(self, request, category=None):
        """Get products by category"""
        products = self.get_queryset().filter(category=category)
        page = self.paginate_queryset(products)
        serializer = ProductListSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)
    
    @extend_schema(
        summary='Get product reviews',
        description='Returns all reviews for a product.',
        tags=['Products']
    )
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """Get all reviews for a product"""
        product = self.get_object()
        reviews = product.reviews.filter(is_verified=True)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary='Add product review',
        description='Add a review to a product (authenticated users only).',
        tags=['Products']
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def add_review(self, request, pk=None):
        """Add a review to a product"""
        product = self.get_object()
        serializer = ReviewSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            serializer.save(product=product, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(summary='List reviews', tags=['Reviews']),
    retrieve=extend_schema(summary='Get review details', tags=['Reviews']),
    create=extend_schema(summary='Create review', tags=['Reviews']),
    update=extend_schema(summary='Update review', tags=['Reviews']),
    partial_update=extend_schema(summary='Partial update review', tags=['Reviews']),
    destroy=extend_schema(summary='Delete review', tags=['Reviews']),
)
class ReviewViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Reviews.
    
    Demonstrates:
    - ModelViewSet
    - User-specific filtering
    - Permission checks
    """
    serializer_class = ReviewSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['product', 'rating', 'is_verified']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Review.objects.all()
        return Review.objects.filter(is_verified=True)
    
    def get_permissions(self):
        if self.action in ['create']:
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return [AllowAny()]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user and not request.user.is_staff:
            return Response(
                {'detail': 'You can only edit your own reviews.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user and not request.user.is_staff:
            return Response(
                {'detail': 'You can only delete your own reviews.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)


@extend_schema_view(
    list=extend_schema(summary='List orders', tags=['Orders']),
    retrieve=extend_schema(summary='Get order details', tags=['Orders']),
    create=extend_schema(summary='Create order', tags=['Orders']),
)
class OrderViewSet(viewsets.ModelViewSet):
    """
    Order management ViewSet.
    
    Demonstrates:
    - Custom create serializer
    - User-specific queryset
    - Custom actions for order status
    """
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all().prefetch_related('items', 'items__product')
        return Order.objects.filter(user=self.request.user).prefetch_related('items')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer
    
    @extend_schema(
        summary='Cancel order',
        description='Cancel a pending order.',
        tags=['Orders']
    )
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an order"""
        order = self.get_object()
        
        if order.status != Order.Status.PENDING:
            return Response(
                {'detail': 'Only pending orders can be cancelled.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Restore stock
        for item in order.items.all():
            item.product.stock += item.quantity
            item.product.save(update_fields=['stock'])
        
        order.status = Order.Status.CANCELLED
        order.save(update_fields=['status'])
        
        return Response({'detail': 'Order cancelled successfully.'})
    
    @extend_schema(
        summary='Update order status',
        description='Update order status (admin only).',
        tags=['Orders']
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def update_status(self, request, pk=None):
        """Update order status (admin only)"""
        order = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(Order.Status.choices):
            return Response(
                {'detail': f'Invalid status. Choose from: {list(dict(Order.Status.choices).keys())}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = new_status
        order.save(update_fields=['status'])
        
        return Response(OrderSerializer(order).data)


# =============================================================================
# GENERIC API VIEWS
# =============================================================================

@extend_schema(
    summary='List and create users',
    tags=['Users']
)
class UserListCreateView(generics.ListCreateAPIView):
    """
    List all users or create a new user.
    
    Demonstrates: ListCreateAPIView
    """
    queryset = User.objects.all()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAdminUser()]


@extend_schema(
    summary='Retrieve, update, delete user',
    tags=['Users']
)
class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a user.
    
    Demonstrates: RetrieveUpdateDestroyAPIView
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        pk = self.kwargs.get('pk')
        if pk == 'me':
            return self.request.user
        return super().get_object()
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance != request.user and not request.user.is_staff:
            return Response(
                {'detail': 'You can only update your own profile.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)


@extend_schema(
    summary='Get or create user profile',
    tags=['Users']
)
class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update user profile.
    
    Demonstrates: RetrieveUpdateAPIView
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


@extend_schema(
    summary='List products (simple)',
    tags=['Products']
)
class ProductListView(generics.ListAPIView):
    """
    Simple product list.
    
    Demonstrates: ListAPIView
    """
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductListSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [AllowAny]


@extend_schema(
    summary='Get product detail (simple)',
    tags=['Products']
)
class ProductDetailView(generics.RetrieveAPIView):
    """
    Simple product detail.
    
    Demonstrates: RetrieveAPIView
    """
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'


# =============================================================================
# API VIEWS (Custom views)
# =============================================================================

@extend_schema(
    summary='Dashboard statistics',
    description='Get dashboard statistics for the current user.',
    tags=['Dashboard']
)
class DashboardView(views.APIView):
    """
    Dashboard statistics API.
    
    Demonstrates: APIView for custom logic
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        data = {
            'user': UserSerializer(user).data,
            'orders': {
                'total': Order.objects.filter(user=user).count(),
                'pending': Order.objects.filter(user=user, status=Order.Status.PENDING).count(),
                'completed': Order.objects.filter(user=user, status=Order.Status.DELIVERED).count(),
            },
            'reviews': {
                'total': Review.objects.filter(user=user).count(),
                'verified': Review.objects.filter(user=user, is_verified=True).count(),
            },
            'spending': {
                'total': float(
                    Order.objects.filter(
                        user=user,
                        status=Order.Status.DELIVERED
                    ).aggregate(total=models.Sum('total_amount'))['total'] or 0
                )
            }
        }
        
        return Response(data)


@extend_schema(
    summary='Search across all entities',
    description='Global search endpoint.',
    tags=['Search'],
    parameters=[
        OpenApiParameter('q', OpenApiTypes.STR, description='Search query', required=True),
        OpenApiParameter('type', OpenApiTypes.STR, description='Filter by type (product, review)'),
    ]
)
class GlobalSearchView(views.APIView):
    """
    Global search endpoint.
    
    Demonstrates: APIView with query parameters
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        query = request.query_params.get('q', '').strip()
        search_type = request.query_params.get('type', 'all')
        
        if len(query) < 2:
            return Response(
                {'detail': 'Search query must be at least 2 characters.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        results = {
            'products': [],
            'reviews': [],
        }
        
        if search_type in ['all', 'product']:
            products = Product.objects.filter(
                Q(name__icontains=query) | Q(description__icontains=query),
                is_active=True
            )[:10]
            results['products'] = ProductListSerializer(products, many=True).data
        
        if search_type in ['all', 'review']:
            reviews = Review.objects.filter(
                Q(title__icontains=query) | Q(content__icontains=query),
                is_verified=True
            )[:10]
            results['reviews'] = ReviewSerializer(reviews, many=True).data
        
        return Response(results)


@extend_schema(
    summary='API health check',
    description='Check API health and status.',
    tags=['System']
)
class HealthCheckView(views.APIView):
    """
    API health check endpoint.
    
    Demonstrates: Simple APIView
    """
    permission_classes = [AllowAny]
    throttle_classes = []  # No throttling for health checks
    
    def get(self, request):
        from django.db import connection
        from django.conf import settings
        
        # Check database
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
            db_status = 'healthy'
        except Exception as e:
            db_status = f'unhealthy: {str(e)}'
        
        return Response({
            'status': 'ok',
            'database': db_status,
            'version': '1.0.0',
            'debug': settings.DEBUG,
        })


@extend_schema(
    summary='API statistics',
    description='Get API usage statistics (admin only).',
    tags=['System']
)
class APIStatsView(views.APIView):
    """
    API statistics endpoint.
    
    Demonstrates: Admin-only APIView
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        return Response({
            'users': User.objects.count(),
            'products': Product.objects.count(),
            'orders': Order.objects.count(),
            'reviews': Review.objects.count(),
            'products_by_category': dict(
                Product.objects.values('category')
                .annotate(count=Count('id'))
                .values_list('category', 'count')
            ),
            'orders_by_status': dict(
                Order.objects.values('status')
                .annotate(count=Count('id'))
                .values_list('status', 'count')
            ),
        })


# =============================================================================
# API KEY MANAGEMENT
# =============================================================================

@extend_schema_view(
    list=extend_schema(summary='List API keys', tags=['API Keys']),
    retrieve=extend_schema(summary='Get API key details', tags=['API Keys']),
    create=extend_schema(summary='Create API key', tags=['API Keys']),
    destroy=extend_schema(summary='Delete API key', tags=['API Keys']),
)
class APIKeyViewSet(viewsets.ModelViewSet):
    """
    API Key management.
    
    Demonstrates: ViewSet with custom create
    """
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    http_method_names = ['get', 'post', 'delete']  # No PUT/PATCH
    
    def get_queryset(self):
        return APIKey.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return APIKeyCreateSerializer
        return APIKeySerializer
    
    @extend_schema(
        summary='Rotate API key',
        description='Generate a new key for an existing API key entry.',
        tags=['API Keys']
    )
    @action(detail=True, methods=['post'])
    def rotate(self, request, pk=None):
        """Rotate (regenerate) an API key"""
        import secrets
        
        api_key = self.get_object()
        api_key.key = secrets.token_hex(32)
        api_key.save(update_fields=['key'])
        
        return Response({
            'detail': 'API key rotated successfully.',
            'key': api_key.key
        })


# Import models for dashboard
from django.db import models
