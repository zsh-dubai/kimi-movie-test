import os
from django.conf import settings
from rest_framework import serializers
from .models import Movie, Genre, Episode


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name']


class EpisodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Episode
        fields = ['id', 'season', 'episode_number', 'title', 'description', 'duration', 'air_date', 'still_url']


class MovieSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    poster_url = serializers.SerializerMethodField()
    class Meta:
        model = Movie
        fields = ['id', 'title', 'original_title', 'poster_url', 'backdrop_url',
                  'rating', 'rating_count', 'release_date', 'movie_type',
                  'genres', 'duration', 'director', 'play_url']
    def get_poster_url(self, obj):
        if not obj.poster_url:
            return ''

        # 提取文件名
        filename = obj.poster_url.split('/')[-1]
        local_path = os.path.join(settings.BASE_DIR, 'static', 'posters', filename)

        # 如果本地存在，返回本地URL
        if os.path.exists(local_path):
            return f'/static/posters/{filename}'

        # 否则返回原URL
        return obj.poster_url

class MovieDetailSerializer(MovieSerializer):
    episodes = EpisodeSerializer(many=True, read_only=True)
    #is_favorite = serializers.SerializerMethodField()
    #user_rating = serializers.SerializerMethodField()

    class Meta(MovieSerializer.Meta):
        fields = MovieSerializer.Meta.fields + [
             'description', 'cast', 'trailer_url', 'play_links',
            'episodes',  'created_at'
        ]
    #'is_favorite', 'user_rating',
    def get_is_favorite(self, obj):
        request = self.context.get('request')
        if not request:
            return False
        user = request.user
        if user.is_authenticated:
            return obj.user_interactions.filter(
                user=user, interaction_type='favorite'
            ).exists()
        return False

    def get_user_rating(self, obj):
        request = self.context.get('request')
        if not request:
            return None
        user = request.user
        if user.is_authenticated:
            interaction = obj.user_interactions.filter(
                user=user, interaction_type='rating'
            ).first()
            return interaction.rating if interaction else None
        return None
