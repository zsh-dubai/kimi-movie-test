from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import UserMovieInteraction, Review
from .serializers import UserMovieInteractionSerializer, ReviewSerializer


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
