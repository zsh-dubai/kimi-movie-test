from rest_framework import serializers
from .models import UserMovieInteraction, Review
from apps.movies.serializers import MovieSerializer


class ReviewSerializer(serializers.ModelSerializer):
    user_nickname = serializers.CharField(source='user.nickname', read_only=True)
    movie_title = serializers.CharField(source='movie.title', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user', 'user_nickname', 'movie', 'movie_title',
                  'content', 'rating', 'likes', 'is_spoiler', 'created_at']
        read_only_fields = ['user', 'likes']


class UserMovieInteractionSerializer(serializers.ModelSerializer):
    movie = MovieSerializer(read_only=True)

    class Meta:
        model = UserMovieInteraction
        fields = ['id', 'movie', 'interaction_type', 'rating', 'timestamp']
        read_only_fields = ['timestamp', 'user']

    def create(self, validated_data):
        movie_id = self.context['request'].data.get('movie')
        if movie_id:
            from apps.movies.models import Movie
            try:
                movie = Movie.objects.get(id=movie_id)
                validated_data['movie'] = movie
            except Movie.DoesNotExist:
                raise serializers.ValidationError('电影不存在')
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
