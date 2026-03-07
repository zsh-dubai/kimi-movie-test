from django.core.management.base import BaseCommand
from django.conf import settings
import requests
import time
from apps.movies.models import Movie, Genre


class Command(BaseCommand):
    help = 'Fix movie genres'

    def handle(self, *args, **options):
        self.stdout.write('Fixing movie genres...')

        for movie in Movie.objects.all():
            try:
                response = requests.get(
                    f"{settings.TMDB_BASE_URL}/movie/{movie.tmdb_id}",
                    params={
                        'api_key': settings.TMDB_API_KEY,
                        'language': settings.TMDB_LANGUAGE,
                    },
                    timeout=5
                )

                if response.status_code == 200:
                    data = response.json()
                    genre_ids = [g['id'] for g in data.get('genres', [])]

                    if genre_ids:
                        genres = Genre.objects.filter(tmdb_id__in=genre_ids)
                        movie.genres.set(genres)
                        self.stdout.write(f'Fixed: {movie.title}')
                else:
                    self.stdout.write(self.style.WARNING(f'Skip: {movie.title}'))

                time.sleep(0.2)  # 限速

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error {movie.title}: {e}'))
                continue

        self.stdout.write(self.style.SUCCESS('Done!'))
