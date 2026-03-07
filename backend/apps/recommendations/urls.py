from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# 创建 router
router = DefaultRouter()

# 注册 ViewSet
# basename 用于反向解析 URL
router.register(r'for-you', views.RecommendationViewSet, basename='for-you')
router.register(r'trending', views.PopularRecommendationViewSet, basename='trending')

urlpatterns = [
    path('', include(router.urls)),
]
