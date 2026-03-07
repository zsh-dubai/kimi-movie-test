from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import UserMovieInteraction, Review
from .serializers import UserMovieInteractionSerializer, ReviewSerializer

#serializer_class = UserMovieInteractionSerializer
#permission_classes = [permissions.IsAuthenticated]
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        queryset = Review.objects.all()
        movie_id = self.request.query_params.get('movie')
        if movie_id:
            queryset = queryset.filter(movie_id=movie_id)
        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class InteractionViewSet(viewsets.ModelViewSet):
    serializer_class = UserMovieInteractionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserMovieInteraction.objects.filter(user=self.request.user)
    @action(detail=False, methods=['post'])
    def toggle_favorite(self, request):
        """切换收藏状态（收藏/取消收藏）"""
        movie_id = request.data.get('movie')

        # 查找是否已收藏
        existing = UserMovieInteraction.objects.filter(
            user=request.user,
            movie_id=movie_id,
            interaction_type='favorite'
        ).first()

        if existing:
            # 已收藏，则取消收藏
            existing.delete()
            return Response({
                'status': 'removed',
                'message': '已取消收藏'
            })
        else:
            # 未收藏，则添加收藏
            interaction = UserMovieInteraction.objects.create(
                user=request.user,
                movie_id=movie_id,
                interaction_type='favorite'
            )
            return Response({
                'status': 'added',
                'message': '收藏成功',
                'interaction': UserMovieInteractionSerializer(interaction).data
            }, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        # 只能操作自己的数据
        return UserMovieInteraction.objects.filter(user=self.request.user)

    def destroy(self, request, pk=None):
        try:
            interaction = self.get_queryset().get(pk=pk)
            interaction.delete()
            return Response({'message': '已移除'})
        except UserMovieInteraction.DoesNotExist:
            return Response({'error': '记录不存在'}, status=404)

    @action(detail=False, methods=['post'])
    def toggle_watchlist(self, request):
        """切换想看状态"""
        movie_id = request.data.get('movie')
        existing = UserMovieInteraction.objects.filter(
            user=request.user,
            movie_id=movie_id,
            interaction_type='watchlist'
        ).first()

        if existing:
            existing.delete()
            return Response({'status': 'removed', 'message': '已取消想看'})
        else:
            interaction = UserMovieInteraction.objects.create(
                user=request.user,
                movie_id=movie_id,
                interaction_type='watchlist'
            )
            return Response({
                'status': 'added',
                'message': '已添加想看',
                'interaction': UserMovieInteractionSerializer(interaction).data
            }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def toggle_watched(self, request):
        """切换已看状态"""
        movie_id = request.data.get('movie')
        existing = UserMovieInteraction.objects.filter(
            user=request.user,
            movie_id=movie_id,
            interaction_type='watched'
        ).first()

        if existing:
            existing.delete()
            return Response({'status': 'removed', 'message': '已取消已看'})
        else:
            interaction = UserMovieInteraction.objects.create(
                user=request.user,
                movie_id=movie_id,
                interaction_type='watched'
            )
            return Response({
                'status': 'added',
                'message': '已标记已看',
                'interaction': UserMovieInteractionSerializer(interaction).data
            }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def check_status(self, request):
        """检查当前用户对指定电影的交互状态"""
        # 检查是否登录
        if not request.user or not request.user.is_authenticated:
            return Response({
                'is_favorite': False,
                'in_watchlist': False,
                'is_watched': False,
            })
        movie_id = request.query_params.get('movie')
        if not movie_id:
            return Response({'error': 'movie parameter required'}, status=400)

        interactions = UserMovieInteraction.objects.filter(
            user=request.user,
            movie_id=movie_id
        )

        return Response({
            'is_favorite': interactions.filter(interaction_type='favorite').exists(),
            'in_watchlist': interactions.filter(interaction_type='watchlist').exists(),
            'is_watched': interactions.filter(interaction_type='watched').exists(),
        })

    def get_queryset(self):
        return UserMovieInteraction.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        # 自定义创建方法，处理重复记录
        movie_id = request.data.get('movie')
        interaction_type = request.data.get('interaction_type')

        # 检查是否已存在
        existing = UserMovieInteraction.objects.filter(
            user=request.user,
            movie_id=movie_id,
            interaction_type=interaction_type
        ).first()

        if existing:
            return Response({
                'message': '已经添加过了',
                'interaction': UserMovieInteractionSerializer(existing).data
            }, status=status.HTTP_200_OK)

        # 创建新记录
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response({
            'message': '添加成功',
            'interaction': serializer.data
        }, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def favorites(self, request):
        favorites = self.get_queryset().filter(interaction_type='favorite')
        serializer = self.get_serializer(favorites, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def history(self, request):
        history = self.get_queryset().filter(
            interaction_type__in=['view', 'watched']
        ).order_by('-timestamp')[:50]
        serializer = self.get_serializer(history, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def watchlist(self, request):
        watchlist = self.get_queryset().filter(interaction_type='watchlist')
        serializer = self.get_serializer(watchlist, many=True)
        return Response(serializer.data)
