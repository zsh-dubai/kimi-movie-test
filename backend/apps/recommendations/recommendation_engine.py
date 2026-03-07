from collections import Counter, defaultdict
from django.db.models import Avg, Count, Q
from apps.movies.models import Movie, Genre
from apps.interactions.models import UserMovieInteraction


class RecommendationEngine:
    def __init__(self, user):
        self.user = user
        self.user_interactions = UserMovieInteraction.objects.filter(user=user)

    def get_user_profile(self):
        """构建用户画像"""
        profile = {
            'favorite_genres': [],
            'favorite_actors': [],
            'preferred_years': [],
            'avg_rating': 0,
            'interaction_weights': {
                'view': 1,
                'watchlist': 3,
                'favorite': 5,
                'watched': 4,
                'rating': 6
            }
        }

        # 获取用户所有交互的电影
        interactions = self.user_interactions.select_related('movie').prefetch_related('movie__genres')

        if not interactions.exists():
            return None

        # 统计类型偏好
        genre_scores = defaultdict(int)
        for interaction in interactions:
            weight = profile['interaction_weights'].get(interaction.interaction_type, 1)
            for genre in interaction.movie.genres.all():
                genre_scores[genre.name] += weight

        profile['favorite_genres'] = sorted(genre_scores.items(), key=lambda x: x[1], reverse=True)[:5]

        # 统计年代偏好
        years = [i.movie.release_date.year for i in interactions if i.movie.release_date]
        if years:
            profile['preferred_years'] = {
                'avg': sum(years) / len(years),
                'range': (min(years), max(years))
            }

        return profile

    def content_based_recommend(self, n=10):
        """基于内容的推荐"""
        profile = self.get_user_profile()
        if not profile:
            return self.get_popular_movies(n)

        # 获取用户已交互的电影ID（排除推荐）
        interacted_ids = set(self.user_interactions.values_list('movie_id', flat=True))

        # 基于类型偏好推荐
        favorite_genres = [g[0] for g in profile['favorite_genres']]

        candidates = Movie.objects.filter(
            genres__name__in=favorite_genres
        ).exclude(
            id__in=interacted_ids
        ).annotate(
            genre_match_count=Count('genres', filter=Q(genres__name__in=favorite_genres)),
            avg_rating=Avg('rating')
        ).order_by('-genre_match_count', '-avg_rating')[:n * 2]

        return list(candidates[:n])

    def collaborative_filtering(self, n=10):
        """基于用户的协同过滤"""
        # 获取当前用户喜欢的电影（高权重交互）
        user_favorites = set(self.user_interactions.filter(
            interaction_type__in=['favorite', 'watched', 'rating']
        ).values_list('movie_id', flat=True))

        if not user_favorites:
            return []

        # 找到有相似喜好的用户
        similar_users = UserMovieInteraction.objects.filter(
            movie_id__in=user_favorites,
            interaction_type__in=['favorite', 'watched']
        ).exclude(user=self.user).values('user').annotate(
            common_count=Count('movie')
        ).filter(common_count__gte=2).order_by('-common_count')[:20]

        if not similar_users:
            return []

        # 获取相似用户喜欢的电影
        similar_user_ids = [u['user'] for u in similar_users]
        recommended = UserMovieInteraction.objects.filter(
            user_id__in=similar_user_ids,
            interaction_type__in=['favorite', 'watched', 'rating']
        ).exclude(movie_id__in=user_favorites).values('movie').annotate(
            score=Count('user')
        ).order_by('-score')[:n]

        movie_ids = [r['movie'] for r in recommended]
        return list(Movie.objects.filter(id__in=movie_ids))

    def get_popular_movies(self, n=10):
        """获取热门电影（冷启动或默认推荐）"""
        return list(Movie.objects.order_by('-rating', '-rating_count')[:n])

    def hybrid_recommend(self, n=10):
        """混合推荐算法"""
        # 获取各算法推荐结果
        content_based = self.content_based_recommend(n=15)
        collaborative = self.collaborative_filtering(n=10)
        popular = self.get_popular_movies(n=5)

        # 加权融合
        scores = defaultdict(float)

        # 基于内容推荐权重 0.5
        for i, movie in enumerate(content_based):
            scores[movie.id] += 0.5 * (1 - i / len(content_based))

        # 协同过滤权重 0.3
        for i, movie in enumerate(collaborative):
            scores[movie.id] += 0.3 * (1 - i / len(collaborative))

        # 热门加权 0.2（避免冷启动问题）
        for i, movie in enumerate(popular):
            scores[movie.id] += 0.2 * (1 - i / len(popular))

        # 排序并返回
        sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)[:n]
        return list(Movie.objects.filter(id__in=sorted_ids))
