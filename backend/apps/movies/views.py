from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Count, Q
from .models import Movie, Genre
from .serializers import MovieSerializer, MovieDetailSerializer, GenreSerializer

class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    print(f"=" * 50)
    #print(f"类加载时查询到的电影数量: {queryset.count()}")
    #for m in queryset.order_by('id')[:10]:
        #print(f"  id={m.id}, title={m.title}")
    print(f"=" * 50)
    serializer_class = MovieSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['movie_type', 'genres']
    search_fields = ['title', 'original_title', 'description', 'director']
    ordering_fields = ['rating', 'release_date', 'created_at']

    def list(self, request, *args, **kwargs):
        print("=" * 50)
        print("list 方法被调用了！")
        queryset = self.get_queryset()
        print(f"查询到 {queryset.count()} 部电影")
        for m in queryset[:5]:
            print(f"  {m.id}: {m.title}")
        print("=" * 50)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MovieDetailSerializer
        return MovieSerializer

    def get_queryset(self):
        queryset = Movie.objects.annotate(
            review_count=Count('reviews'),
            avg_rating=Avg('reviews__rating')
        )
        #print(f"API请求时查询: {queryset.count()} 部")
        #for m in queryset.order_by('id')[:10]:
            #print(f"  API查询: id={m.id}, title={m.title}")
        genre = self.request.query_params.get('genre')
        if genre:
            queryset = queryset.filter(genres__name=genre)
        movie_type = self.request.query_params.get('movie_type')
        if movie_type:
            if movie_type == 'anime':
                # 动漫 = 动画类型
                queryset = queryset.filter(genres__name='动画')
            elif movie_type == 'movie':
                # 电影 = 排除电视剧类型（如果有的话）
                # 暂时显示所有，因为目前只有电影数据
                pass
            elif movie_type == 'tv':
                # 电视剧 - 当前数据库可能没有，先返回空
                queryset = queryset.none()
        year = self.request.query_params.get('year')
        if year:
            queryset = queryset.filter(release_date__year=year)

        min_rating = self.request.query_params.get('min_rating')
        if min_rating:
            queryset = queryset.filter(rating__gte=min_rating)

        return queryset.distinct()

    @action(detail=True, methods=['post'])
    def rate(self, request, pk=None):
        movie = self.get_object()
        rating = request.data.get('rating')

        if not rating or not (0 <= float(rating) <= 10):
            return Response({'error': '评分必须在0-10之间'}, status=status.HTTP_400_BAD_REQUEST)

        interaction, created = request.user.interactions.update_or_create(
            movie=movie,
            interaction_type='rating',
            defaults={'rating': rating}
        )

        avg = movie.user_interactions.filter(
            interaction_type='rating'
        ).aggregate(Avg('rating'))['rating__avg'] or 0

        movie.rating = round(avg, 1)
        movie.rating_count = movie.user_interactions.filter(interaction_type='rating').count()
        movie.save()

        return Response({
            'message': '评分成功',
            'new_rating': movie.rating,
            'user_rating': rating
        })

    @action(detail=True, methods=['post'])
    def toggle_favorite(self, request, pk=None):
        movie = self.get_object()
        interaction, created = request.user.interactions.get_or_create(
            movie=movie,
            interaction_type='favorite'
        )

        if not created:
            interaction.delete()
            return Response({'status': 'removed', 'message': '已取消收藏'})

        return Response({'status': 'added', 'message': '已添加收藏'})

    @action(detail=False, methods=['get'])
    def trending(self, request):
        from django.utils import timezone
        from datetime import timedelta

        last_week = timezone.now() - timedelta(days=7)
        trending = Movie.objects.filter(
            user_interactions__timestamp__gte=last_week,
            user_interactions__interaction_type='view'
        ).annotate(
            view_count=Count('user_interactions')
        ).order_by('-view_count')[:10]

        serializer = self.get_serializer(trending, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_genre(self, request):
        genres = Genre.objects.prefetch_related('movies')
        data = []
        for genre in genres[:8]:
            movies = genre.movies.order_by('-rating')[:6]
            data.append({
                'genre': GenreSerializer(genre).data,
                'movies': MovieSerializer(movies, many=True).data
            })
        return Response(data)


class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
