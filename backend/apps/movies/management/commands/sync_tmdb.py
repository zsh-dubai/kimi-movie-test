from django.core.management.base import BaseCommand
from django.conf import settings
import requests
import time
from apps.movies.models import Movie, Genre


class Command(BaseCommand):
    help = '从 TMDB 同步热门电影数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--pages',
            type=int,
            default=5,
            help='同步多少页数据（每页20部）'
        )

    def handle(self, *args, **options):
        api_key = settings.TMDB_API_KEY
        if not api_key:
            self.stdout.write(self.style.ERROR('错误：TMDB_API_KEY 未配置'))
            return

        pages = options['pages']
        base_url = settings.TMDB_BASE_URL

        self.stdout.write(self.style.SUCCESS(f'开始同步 {pages} 页电影数据...'))

        total_created = 0
        total_updated = 0

        for page in range(1, pages + 1):
            self.stdout.write(f'正在获取第 {page}/{pages} 页...')

            # 重试机制
            max_retries = 3
            retry_count = 0
            success = False
            response = None  # ← 初始化response

            while retry_count < max_retries and not success:
                try:
                    response = requests.get(
                        f'{base_url}/movie/popular',
                        params={
                            'api_key': api_key,
                            'language': settings.TMDB_LANGUAGE,
                            'page': page
                        },
                        timeout=10
                    )
                    success = True

                except requests.exceptions.ConnectionError as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        self.stdout.write(self.style.ERROR(f'第 {page} 页连接失败，已重试{max_retries}次，跳过'))
                        break
                    self.stdout.write(self.style.WARNING(f'连接失败，{2 ** retry_count}秒后重试...'))
                    time.sleep(2 ** retry_count)
                    continue

                except requests.exceptions.Timeout:
                    retry_count += 1
                    if retry_count >= max_retries:
                        self.stdout.write(self.style.ERROR(f'第 {page} 页请求超时，跳过'))
                        break
                    self.stdout.write(self.style.WARNING(f'请求超时，{2 ** retry_count}秒后重试...'))
                    time.sleep(2 ** retry_count)
                    continue

            if not success or response is None:  # ← 增加response为None的检查
                continue

            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f'第 {page} 页请求失败: {response.status_code}'))
                continue

            data = response.json()
            movies = data.get('results', [])

            for movie_data in movies:
                try:  # ← 增加单部电影异常处理
                    # 处理类型
                    genre_ids = movie_data.get('genre_ids', [])

                    # 创建或更新电影
                    movie, created = Movie.objects.update_or_create(
                        tmdb_id=movie_data['id'],
                        defaults={
                            'title': movie_data.get('title', ''),
                            'original_title': movie_data.get('original_title', ''),
                            'description': movie_data.get('overview', ''),
                            'poster_url': f"{settings.TMDB_IMAGE_BASE_URL}/w500{movie_data.get('poster_path', '')}" if movie_data.get(
                                'poster_path') else '',
                            'backdrop_url': f"{settings.TMDB_IMAGE_BASE_URL}/w1280{movie_data.get('backdrop_path', '')}" if movie_data.get(
                                'backdrop_path') else '',
                            'rating': movie_data.get('vote_average', 0),
                            'rating_count': movie_data.get('vote_count', 0),
                            'release_date': movie_data.get('release_date') or None,
                        }
                    )

                    # 关联类型
                    if genre_ids:
                        genres = Genre.objects.filter(tmdb_id__in=genre_ids)
                        movie.genres.set(genres)

                    if created:
                        total_created += 1
                    else:
                        total_updated += 1

                except Exception as e:  # ← 单部电影失败不中断整体
                    self.stdout.write(self.style.ERROR(f'处理电影 {movie_data.get("title", "Unknown")} 失败: {e}'))
                    continue

            self.stdout.write(self.style.SUCCESS(f'第 {page} 页完成，本页处理 {len(movies)} 部'))

            # 限速：增加到1秒更保险
            if page < pages:
                time.sleep(1)  # ← 从0.5秒改为1秒

        self.stdout.write(self.style.SUCCESS(
            f'\n同步完成！新增: {total_created} 部, 更新: {total_updated} 部'
        ))
