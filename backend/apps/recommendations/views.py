from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.db.models import Avg, Count, Q
from apps.movies.models import Movie
from apps.movies.serializers import MovieSerializer
from apps.interactions.models import UserMovieInteraction
import random


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def for_you(request):
    """为你推荐"""
    try:
        user = request.user
        num = int(request.query_params.get('limit', 10))

        # 检查用户是否有评分记录
        has_ratings = UserMovieInteraction.objects.filter(
            user=user,
            interaction_type='rating'
        ).exists()

        if has_ratings:
            # 个性化推荐
            # 获取用户喜欢的类型（评分>=7）
            liked_genres = set()
            user_ratings = UserMovieInteraction.objects.filter(
                user=user,
                interaction_type='rating',
                rating__gte=7
            ).select_related('movie')

            for r in user_ratings:
                liked_genres.update(r.movie.genres.values_list('id', flat=True))

            # 基于内容的推荐
            content_based = []
            if liked_genres:
                content_based = list(Movie.objects.filter(
                    genres__id__in=liked_genres
                ).exclude(
                    user_interactions__user=user,
                    user_interactions__interaction_type__in=['view', 'watched']
                ).distinct()[:num // 2])

            # 热门补充
            needed = num - len(content_based)
            existing_ids = [m.id for m in content_based]
            popular = list(Movie.objects.exclude(
                id__in=existing_ids
            ).order_by('-rating')[:max(needed, 5)])

            # 合并
            recommendations = content_based + popular
            random.shuffle(recommendations)

            serializer = MovieSerializer(recommendations[:num], many=True, context={'request': request})
            return Response({
                'recommendations': serializer.data,
                'algorithm': 'hybrid',
                'content_based': len(content_based),
                'popular': len(popular)
            })
        else:
            # 新用户：返回高分热门
            movies = Movie.objects.order_by('-rating')[:10]
            serializer = MovieSerializer(movies, many=True, context={'request': request})
            return Response({
                'recommendations': serializer.data,
                'algorithm': 'popular_for_new_user'
            })

    except Exception as e:
        print(f"推荐错误: {str(e)}")
        # 出错时返回热门
        movies = Movie.objects.order_by('-rating')[:10]
        serializer = MovieSerializer(movies, many=True, context={'request': request})
        return Response({
            'recommendations': serializer.data,
            'algorithm': 'error_fallback'
        })


@api_view(['GET'])
@permission_classes([AllowAny])
def similar_movies(request, movie_id):
    """相似电影"""
    try:
        from apps.movies.models import Movie
        target = Movie.objects.get(id=movie_id)

        similar = Movie.objects.filter(
            Q(genres__in=target.genres.all()) |
            Q(director=target.director)
        ).exclude(id=movie_id).annotate(
            similarity_score=Count('genres', filter=Q(genres__in=target.genres.all()))
        ).order_by('-similarity_score', '-rating')[:8]

        serializer = MovieSerializer(similar, many=True, context={'request': request})
        return Response(serializer.data)
    except Movie.DoesNotExist:
        return Response({'error': '电影不存在'}, status=404)


@api_view(['GET'])
@permission_classes([AllowAny])
def trending_movies(request):
    """热门趋势"""
    from django.utils import timezone
    from datetime import timedelta

    last_week = timezone.now() - timedelta(days=7)

    trending = Movie.objects.filter(
        user_interactions__timestamp__gte=last_week,
        user_interactions__interaction_type='view'
    ).annotate(
        view_count=Count('user_interactions')
    ).order_by('-view_count')[:10]

    serializer = MovieSerializer(trending, many=True, context={'request': request})
    return Response(serializer.data)
