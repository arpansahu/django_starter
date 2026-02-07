"""
API App URLs with Router
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'api_app'

# DRF Router for ViewSets
router = DefaultRouter()
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'reviews', views.ReviewViewSet, basename='review')
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'api-keys', views.APIKeyViewSet, basename='api-key')

urlpatterns = [
    # ViewSet routes
    path('', include(router.urls)),
    
    # Generic API Views
    path('users/', views.UserListCreateView.as_view(), name='user-list'),
    path('users/<str:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    
    # Simple product views (alternative to ViewSet)
    path('products-simple/', views.ProductListView.as_view(), name='product-list-simple'),
    path('products-simple/<slug:slug>/', views.ProductDetailView.as_view(), name='product-detail-simple'),
    
    # Custom API Views
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('search/', views.GlobalSearchView.as_view(), name='global-search'),
    path('health/', views.HealthCheckView.as_view(), name='health-check'),
    path('stats/', views.APIStatsView.as_view(), name='api-stats'),
]
