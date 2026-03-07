from django.core.management.base import BaseCommand
from django.conf import settings
import requests
from apps.movies.models import Genre


class Command(BaseCommand):
    help = 'Sync movie genres from TMDB'

    def handle(self, *args, **options):
        api_key = settings.TMDB_API_KEY
        base_url = settings.TMDB_BASE_URL

        self.stdout.write('Fetching genres from TMDB...')

        response = requests.get(
            f'{base_url}/genre/movie/list',
            params={
                'api_key': api_key,
                'language': settings.TMDB_LANGUAGE,
            }
        )

        if response.status_code != 200:
            self.stdout.write(self.style.ERROR(f'Failed: {response.status_code}'))
            return

        genres = response.json().get('genres', [])

        created = 0
        for g in genres:
            obj, is_new = Genre.objects.update_or_create(
                tmdb_id=g['id'],
                defaults={'name': g['name']}
            )
            if is_new:
                created += 1
                self.stdout.write(f'Created: {g["name"]}')

        self.stdout.write(self.style.SUCCESS(f'Done: {len(genres)} total, {created} new'))
