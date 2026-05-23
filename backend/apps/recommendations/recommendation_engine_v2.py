from collections import Counter, defaultdict
from django.db.models import Avg, Count, Q, F
from apps.movies.models import Movie, Genre
from apps.interactions.models import UserMovieInteraction
import math


class ExplainableRecommendationEngine:
    """可解释推荐引擎（毕业设计版）"""

    def __init__(self, user):
        self.user = user
        self.user_interactions = UserMovieInteraction.objects.filter(user=user)
        self.interacted_movie_ids = set(self.user_interactions.values_list('movie_id', flat=True))

    def get_user_stats(self):
        """获取用户交互统计"""
        stats = {
            'total_interactions': self.user_interactions.count(),
            'ratings_count': self.user_interactions.filter(interaction_type='rating').count(),
            'favorites_count': self.user_interactions.filter(interaction_type='favorite').count(),
            'watched_count': self.user_interactions.filter(interaction_type='watched').count(),
            'watchlist_count': self.user_interactions.filter(interaction_type='watchlist').count(),
        }
        return stats

    def get_user_profile(self):
        """构建详细用户画像（用于可视化）"""
        profile = {
            'favorite_genres': [],
            'genre_distribution': [],
            'interaction_timeline': [],
            'rating_distribution': [],
            'avg_user_rating': 0,
        }

        interactions = self.user_interactions.select_related('movie').prefetch_related('movie__genres')

        if not interactions.exists():
            return None

        # 类型偏好统计（带权重）
        genre_scores = defaultdict(int)
        genre_counts = Counter()

        for interaction in interactions:
            weight = self._get_interaction_weight(interaction.interaction_type)
            for genre in interaction.movie.genres.all():
                genre_scores[genre.name] += weight
                genre_counts[genre.name] += 1

        total_score = sum(genre_scores.values()) or 1

        profile['favorite_genres'] = [
            {
                'genre': name,
                'score': score,
                'count': genre_counts[name],
                'percentage': round(score / total_score * 100, 1)
            }
            for name, score in sorted(genre_scores.items(), key=lambda x: x[1], reverse=True)[:8]
        ]

        # 简化：只保留类型分布
        profile['genre_distribution'] = profile['favorite_genres']

        # 用户平均评分
        ratings = self.user_interactions.filter(rating__isnull=False).values_list('rating', flat=True)
        if ratings:
            profile['avg_user_rating'] = round(sum(ratings) / len(ratings), 1)

        return profile

    def _get_interaction_weight(self, interaction_type):
        """交互类型权重"""
        weights = {
            'view': 1,
            'watchlist': 3,
            'favorite': 5,
            'watched': 4,
            'rating': 6
        }
        return weights.get(interaction_type, 1)

    def _get_user_type(self):
        """判断用户类型（用于分层策略）"""
        stats = self.get_user_stats()
        total = stats['total_interactions']

        if total == 0:
            return 'cold_start', '全新用户，暂无观影记录'
        elif total < 5:
            return 'warm_start', f'新用户，仅有 {total} 次交互'
        elif stats['ratings_count'] < 3:
            return 'semi_active', f'活跃用户，但评分数据不足（仅{stats["ratings_count"]}次评分）'
        else:
            return 'active', f'成熟用户，{stats["ratings_count"]}次评分'

    def get_popular_movies(self, n=10, exclude_ids=None):
        """获取热门电影（带解释）"""
        if exclude_ids is None:
            exclude_ids = set()

        movies = Movie.objects.exclude(id__in=exclude_ids).order_by('-rating', '-rating_count')[:n]

        recommendations = []
        for i, movie in enumerate(movies):
            recommendations.append({
                'movie': movie,
                'explanation': '近期热门高分电影，适合新用户探索',
                'algorithm': 'cold_start_popular',
                'confidence': round(0.9 - i * 0.05, 2),  # 排名越靠前置信度越高
                'reasons': [
                    {'type': 'popular', 'detail': f'评分 {movie.rating}', 'weight': 0.5},
                    {'type': 'trending', 'detail': f'{movie.rating_count}人评分', 'weight': 0.3}
                ]
            })

        return recommendations

    def content_based_recommend(self, n=10):
        """基于内容的推荐（带详细解释）"""
        profile = self.get_user_profile()
        if not profile:
            return []

        favorite_genres = [g['genre'] for g in profile['favorite_genres'][:5]]
        if not favorite_genres:
            return []

        # 获取候选电影
        candidates = Movie.objects.filter(
            genres__name__in=favorite_genres
        ).exclude(
            id__in=self.interacted_movie_ids
        ).annotate(
            genre_match_count=Count('genres', filter=Q(genres__name__in=favorite_genres)),
            avg_rating=Avg('user_interactions__rating')
        ).distinct()

        # 计算每部电影的匹配分数
        scored_movies = []
        for movie in candidates[:n * 3]:  # 先取多一些再排序
            score, reasons = self._calculate_content_score(movie, profile, favorite_genres)
            scored_movies.append((movie, score, reasons))

        # 按分数排序
        scored_movies.sort(key=lambda x: x[1], reverse=True)

        recommendations = []
        for i, (movie, score, reasons) in enumerate(scored_movies[:n]):
            # 构建解释文本
            top_reasons = sorted(reasons, key=lambda x: x['weight'], reverse=True)[:2]
            reason_text = '、'.join([r['detail'] for r in top_reasons])

            recommendations.append({
                'movie': movie,
                'explanation': f"基于你喜欢的类型：{reason_text}",
                'algorithm': 'content_based',
                'confidence': round(min(score, 1.0), 2),
                'reasons': reasons
            })

        return recommendations

    def _calculate_content_score(self, movie, profile, favorite_genres):
        """计算内容匹配分数和原因"""
        reasons = []
        total_score = 0

        # 1. 类型匹配分数
        movie_genres = [g.name for g in movie.genres.all()]
        matched_genres = set(movie_genres) & set(favorite_genres)

        if matched_genres:
            genre_weight = len(matched_genres) / len(favorite_genres)
            genre_score = genre_weight * 0.5  # 类型匹配占50%
            total_score += genre_score

            for genre in matched_genres:
                # 找到该类型的用户偏好分数
                genre_pref = next((g for g in profile['favorite_genres'] if g['genre'] == genre), None)
                if genre_pref:
                    reasons.append({
                        'type': 'genre_match',
                        'detail': genre,
                        'weight': round(genre_pref['percentage'] / 100 * 0.5, 3)
                    })

        # 2. 评分分数
        if movie.rating and movie.rating >= 7.0:
            rating = float(movie.rating) if movie.rating else 0
            if rating >= 7.0:
                rating_score = min((rating - 6) / 4, 1.0) * 0.3 #评分占30%
            total_score += rating_score
            reasons.append({
                'type': 'high_rating',
                'detail': f'评分 {movie.rating}',
                'weight': round(rating_score, 3)
            })

        # 3. 热度分数
        if movie.rating_count and movie.rating_count > 50:
            popularity_score = min(movie.rating_count / 500, 1.0) * 0.2  # 热度占20%
            total_score += popularity_score
            reasons.append({
                'type': 'popularity',
                'detail': f'{movie.rating_count}人评分',
                'weight': round(popularity_score, 3)
            })

        return total_score, reasons

    def collaborative_filtering(self, n=10):
        """基于用户的协同过滤（带解释）"""
        # 获取用户喜欢的电影
        user_favorites = set(self.user_interactions.filter(
            interaction_type__in=['favorite', 'watched', 'rating']
        ).values_list('movie_id', flat=True))

        if not user_favorites:
            return []

        # 找到相似用户
        similar_users = UserMovieInteraction.objects.filter(
            movie_id__in=user_favorites,
            interaction_type__in=['favorite', 'watched', 'rating']
        ).exclude(user=self.user).values('user').annotate(
            common_count=Count('movie'),
            common_movies=Count('movie', distinct=True)
        ).filter(common_count__gte=2).order_by('-common_count')[:20]

        if not similar_users:
            return []

        # 收集相似用户数据
        similar_user_ids = [u['user'] for u in similar_users]
        similarity_scores = {u['user']: u['common_count'] for u in similar_users}
        max_common = max(similarity_scores.values()) if similarity_scores else 1

        # 获取相似用户喜欢的电影
        candidates = UserMovieInteraction.objects.filter(
            user_id__in=similar_user_ids,
            interaction_type__in=['favorite', 'watched', 'rating']
        ).exclude(
            movie_id__in=user_favorites
        ).values('movie').annotate(
            similar_user_count=Count('user', distinct=True),
            total_score=Count('user')
        ).order_by('-similar_user_count', '-total_score')[:n * 2]

        recommendations = []
        for item in candidates[:n]:
            movie = Movie.objects.get(id=item['movie'])
            similar_count = item['similar_user_count']

            # 计算置信度（基于相似用户数量和共同电影比例）
            confidence = min(similar_count / 5, 1.0) * 0.8 + 0.2

            recommendations.append({
                'movie': movie,
                'explanation': f"与你兴趣相似的用户也喜欢这部电影",
                'algorithm': 'collaborative_filtering',
                'confidence': round(confidence, 2),
                'reasons': [
                    {
                        'type': 'similar_users',
                        'detail': f'{similar_count}位相似用户推荐',
                        'weight': round(confidence * 0.7, 3)
                    },
                    {
                        'type': 'community_choice',
                        'detail': '社区热门选择',
                        'weight': round(0.3, 3)
                    }
                ],
                'similar_user_count': similar_count
            })

        return recommendations

    def hybrid_recommend(self, n=10):
        """分层混合推荐（核心方法）"""
        user_type, user_type_desc = self._get_user_type()

        result = {
            'user_type': user_type,
            'user_type_description': user_type_desc,
            'user_profile': self.get_user_profile(),
            'algorithm_breakdown': {},  # 各算法贡献比例
            'recommendations': []
        }

        all_recommendations = []

        if user_type == 'cold_start':
            # 冷启动：100% 热门推荐
            result['algorithm_breakdown'] = {'cold_start_popular': 1.0}
            all_recommendations = self.get_popular_movies(n=n)

        elif user_type == 'warm_start':
            # 半冷启动：70% 内容 + 30% 热门
            result['algorithm_breakdown'] = {'content_based': 0.7, 'cold_start_popular': 0.3}
            content_recs = self.content_based_recommend(n=int(n * 0.7))
            popular_recs = self.get_popular_movies(
                n=n - len(content_recs),
                exclude_ids={r['movie'].id for r in content_recs}
            )
            all_recommendations = content_recs + popular_recs

        else:
            # 活跃用户：50% 内容 + 30% 协同 + 20% 热门
            result['algorithm_breakdown'] = {
                'content_based': 0.5,
                'collaborative_filtering': 0.3,
                'cold_start_popular': 0.2
            }
            content_recs = self.content_based_recommend(n=int(n * 0.5))
            collab_recs = self.collaborative_filtering(n=int(n * 0.3))
            popular_recs = self.get_popular_movies(
                n=n - len(content_recs) - len(collab_recs),
                exclude_ids={r['movie'].id for r in content_recs + collab_recs}
            )
            all_recommendations = content_recs + collab_recs + popular_recs

        # 去重并排序
        seen = set()
        final_recs = []
        for rec in all_recommendations:
            movie_id = rec['movie'].id
            if movie_id not in seen:
                seen.add(movie_id)
                final_recs.append(rec)

        # 按置信度排序
        final_recs.sort(key=lambda x: x['confidence'], reverse=True)
        result['recommendations'] = final_recs[:n]

        return result
