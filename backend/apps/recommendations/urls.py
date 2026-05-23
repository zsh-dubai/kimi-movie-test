from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecommendationViewSet, PopularRecommendationViewSet

router = DefaultRouter()
router.register(r'for-you', RecommendationViewSet, basename='recommendations')
router.register(r'popular', PopularRecommendationViewSet, basename='popular')

urlpatterns = [
    path('', include(router.urls)),
]
