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

    class Meta:
        model = Movie
        fields = ['id', 'title', 'original_title', 'poster_url', 'backdrop_url',
                  'rating', 'rating_count', 'release_date', 'movie_type',
                  'genres', 'duration', 'director', 'play_url']


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
