from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'reviews', views.ReviewViewSet, basename='review')  # 添加 basename
router.register(r'my', views.InteractionViewSet, basename='interaction')

urlpatterns = [
    path('', include(router.urls)),
]
