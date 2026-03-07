from django.core.management.base import BaseCommand
from apps.movies.models import Movie


class Command(BaseCommand):
    help = 'Update play URLs for movies'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, help='CSV file with movie_id,play_url')

    def handle(self, *args, **options):
        # 示例：手动给前10部电影添加示例链接
        # 实际使用时可以从文件读取或手动编辑

        updates = [
            # (电影ID, 播放链接)
            (1, 'https://www.example.com/play/movie1'),
            (2, 'https://www.example.com/play/movie2'),
            # 或者批量更新：给所有电影添加搜索链接作为默认值
        ]

        # 或者：给所有空链接的电影添加默认搜索链接
        base_url = 'https://www.cupfox.app/search?key='

        count = 0
        for movie in Movie.objects.filter(play_url__isnull=True) | Movie.objects.filter(play_url=''):
            search_url = base_url + movie.title
            movie.play_url = search_url
            movie.save()
            count += 1
            self.stdout.write(f'Updated: {movie.title} -> {search_url}')

        self.stdout.write(self.style.SUCCESS(f'Updated {count} movies'))
