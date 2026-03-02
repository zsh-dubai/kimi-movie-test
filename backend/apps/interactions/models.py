from django.db import models
from django.conf import settings


class UserMovieInteraction(models.Model):
    INTERACTION_TYPES = [
        ('view', '浏览'),
        ('rating', '评分'),
        ('favorite', '收藏'),
        ('watchlist', '想看'),
        ('watched', '已看'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='interactions')
    movie = models.ForeignKey('movies.Movie', on_delete=models.CASCADE, related_name='user_interactions')
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    rating = models.FloatField(null=True, blank=True, verbose_name='评分(1-10)')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_interactions'
        unique_together = ['user', 'movie', 'interaction_type']

    def __str__(self):
        return f"{self.user.username} - {self.movie.title} - {self.interaction_type}"


class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    movie = models.ForeignKey('movies.Movie', on_delete=models.CASCADE, related_name='reviews')
    content = models.TextField(verbose_name='评论内容')
    rating = models.FloatField(verbose_name='评分')
    likes = models.IntegerField(default=0, verbose_name='点赞数')
    is_spoiler = models.BooleanField(default=False, verbose_name='包含剧透')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reviews'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} 评论 {self.movie.title}"
