from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .recommendation_engine import RecommendationEngine
from apps.movies.serializers import MovieSerializer


class RecommendationViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    # 用 list 方法处理 GET /for-you/
    def list(self, request):
        """个性化推荐（混合算法）"""
        engine = RecommendationEngine(request.user)
        recommendations = engine.hybrid_recommend(n=20)

        serializer = MovieSerializer(recommendations, many=True, context={'request': request})
        return Response({
            'algorithm': 'hybrid',
            'recommendations': serializer.data
        })


class PopularRecommendationViewSet(viewsets.ViewSet):
    """用于未登录用户的热门推荐"""
    permission_classes = [permissions.AllowAny]

    def list(self, request):
        engine = RecommendationEngine(None)
        popular = engine.get_popular_movies(n=20)
        serializer = MovieSerializer(popular, many=True, context={'request': request})
        return Response({
            'algorithm': 'popular_for_new_user',
            'recommendations': serializer.data
        })
