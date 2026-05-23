import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.movies.models import Movie
from apps.interactions.models import UserMovieInteraction

User = get_user_model()


class Command(BaseCommand):
    help = '生成模拟用户数据用于展示协同过滤效果'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=50, help='生成的用户数量')
        parser.add_argument('--interactions', type=int, default=15, help='每个用户的交互数量')

    def handle(self, *args, **options):
        user_count = options['users']
        interaction_count = options['interactions']

        # 获取所有电影
        movies = list(Movie.objects.all())
        if not movies:
            self.stdout.write(self.style.ERROR('数据库中没有电影，请先导入数据'))
            return

        self.stdout.write(f'开始生成 {user_count} 个模拟用户...')

        created_users = []
        for i in range(user_count):
            username = f'demo_user_{i+1}'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'password': 'demo123456',
                    'nickname': f'测试用户{i+1}'
                }
            )
            if created:
                user.set_password('demo123456')
                user.save()
            created_users.append(user)

        self.stdout.write(f'成功创建/获取 {len(created_users)} 个用户')

        # 为每个用户生成随机交互
        interaction_types = ['view', 'watchlist', 'favorite', 'watched', 'rating']
        total_created = 0

        for user in created_users:
            # 随机选择电影（不重复）
            selected_movies = random.sample(movies, min(interaction_count, len(movies)))

            for movie in selected_movies:
                # 随机交互类型（评分概率更高，便于协同过滤）
                weights = [0.2, 0.15, 0.2, 0.15, 0.3]  # view, watchlist, favorite, watched, rating
                interaction_type = random.choices(interaction_types, weights=weights)[0]

                # 评分数据
                rating = None
                if interaction_type == 'rating':
                    # 根据电影类型偏好给分（模拟真实偏好）
                    rating = round(random.uniform(3.0, 10.0), 1)

                # 创建交互记录
                interaction, created = UserMovieInteraction.objects.get_or_create(
                    user=user,
                    movie=movie,
                    interaction_type=interaction_type,
                    defaults={'rating': rating}
                )

                if created:
                    total_created += 1

        self.stdout.write(self.style.SUCCESS(
            f'完成！共创建 {total_created} 条交互记录，'
            f'平均每个用户 {total_created // len(created_users)} 条'
        ))
