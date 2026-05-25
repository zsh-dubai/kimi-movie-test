import os
import requests
from django.core.management.base import BaseCommand
from apps.movies.models import Movie


class Command(BaseCommand):
    help = '下载电影海报到本地 static/posters 目录'

    def handle(self, *args, **options):
        # 确保目录存在
        posters_dir = os.path.join('static', 'posters')
        os.makedirs(posters_dir, exist_ok=True)

        # 获取所有有海报URL的电影
        movies = Movie.objects.exclude(poster_url='').exclude(poster_url__isnull=True)
        total = movies.count()

        self.stdout.write(self.style.SUCCESS(f'开始下载 {total} 部电影海报...'))

        downloaded = 0
        skipped = 0
        failed = 0

        for i, movie in enumerate(movies, 1):
            # 从URL提取文件名
            url = movie.poster_url
            filename = url.split('/')[-1]
            filepath = os.path.join(posters_dir, filename)

            # 已存在则跳过
            if os.path.exists(filepath):
                skipped += 1
                if i % 100 == 0:
                    self.stdout.write(f'进度: {i}/{total} (跳过 {skipped})')
                continue

            try:
                response = requests.get(url, timeout=15)
                if response.status_code == 200:
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    downloaded += 1
                    if i % 50 == 0:
                        self.stdout.write(f'进度: {i}/{total} (已下载 {downloaded})')
                else:
                    failed += 1
                    self.stdout.write(self.style.WARNING(f'下载失败 [{response.status_code}]: {movie.title}'))
            except Exception as e:
                failed += 1
                self.stdout.write(self.style.ERROR(f'错误: {movie.title} - {e}'))

        self.stdout.write(self.style.SUCCESS(
            f'\n完成！总计: {total}, 下载: {downloaded}, 跳过: {skipped}, 失败: {failed}'
        ))
