from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .recommendation_engine_v2 import ExplainableRecommendationEngine
from apps.movies.serializers import MovieSerializer


class RecommendationViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """个性化推荐（可解释版本）"""
        engine = ExplainableRecommendationEngine(request.user)
        result = engine.hybrid_recommend(n=20)

        # 序列化电影数据
        recommendations_data = []
        for rec in result['recommendations']:
            movie_data = MovieSerializer(rec['movie'], context={'request': request}).data
            recommendations_data.append({
                'movie': movie_data,
                'explanation': rec['explanation'],
                'algorithm': rec['algorithm'],
                'confidence': rec['confidence'],
                'reasons': rec['reasons']
            })

        return Response({
            'user_type': result['user_type'],
            'user_type_description': result['user_type_description'],
            'user_profile': result['user_profile'],
            'algorithm_breakdown': result['algorithm_breakdown'],
            'recommendations': recommendations_data
        })

    @action(detail=False, methods=['get'])
    def profile(self, request):
        """获取用户画像（用于可视化展示）"""
        engine = ExplainableRecommendationEngine(request.user)
        profile = engine.get_user_profile()
        stats = engine.get_user_stats()

        return Response({
            'profile': profile,
            'stats': stats,
            'user_type': engine._get_user_type()[0],
            'user_type_description': engine._get_user_type()[1]
        })


class PopularRecommendationViewSet(viewsets.ViewSet):
    """未登录用户的热门推荐"""
    permission_classes = [permissions.AllowAny]

    def list(self, request):
        engine = ExplainableRecommendationEngine(None)
        popular = engine.get_popular_movies(n=20)

        recommendations_data = []
        for rec in popular:
            movie_data = MovieSerializer(rec['movie'], context={'request': request}).data
            recommendations_data.append({
                'movie': movie_data,
                'explanation': rec['explanation'],
                'algorithm': rec['algorithm'],
                'confidence': rec['confidence'],
                'reasons': rec['reasons']
            })

        return Response({
            'algorithm': 'cold_start_popular',
            'user_type': 'guest',
            'recommendations': recommendations_data
        })
