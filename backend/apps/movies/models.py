from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Genre(models.Model):
    tmdb_id = models.IntegerField(unique=True, null=True, blank=True)
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'genres'

    def __str__(self):
        return self.name


class Movie(models.Model):
    tmdb_id = models.IntegerField(unique=True, null=True, blank=True, verbose_name='TMDB ID')
    MOVIE_TYPES = [('movie', '电影'), ('tv', '电视剧'), ('anime', '动漫')]

    title = models.CharField(max_length=200, verbose_name='标题')
    original_title = models.CharField(max_length=200, blank=True, verbose_name='原名')
    description = models.TextField(verbose_name='简介')
    movie_type = models.CharField(max_length=10, choices=MOVIE_TYPES, default='movie')
    genres = models.ManyToManyField(Genre, related_name='movies')

    release_date = models.DateField(null=True, blank=True, verbose_name='上映日期')
    duration = models.IntegerField(null=True, blank=True, verbose_name='时长(分钟)')
    rating_count = models.IntegerField(default=0, verbose_name='评分人数')

    poster_url = models.URLField(max_length=500, blank=True, verbose_name='海报')
    backdrop_url = models.URLField(max_length=500, blank=True, verbose_name='背景图')
    trailer_url = models.URLField(max_length=500, blank=True, verbose_name='预告片')

    director = models.CharField(max_length=200, blank=True, verbose_name='导演')
    cast = models.JSONField(default=list, verbose_name='演员阵容')
    play_links = models.JSONField(default=dict, verbose_name='播放链接')
    play_url = models.URLField(max_length=500, blank=True, null=True, verbose_name='播放链接')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rating = models.DecimalField(
        max_digits=3,  # 最大位数（如 10.0）
        decimal_places=1,  # 小数位数
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        verbose_name='评分'
    )

    def save(self, *args, **kwargs):
        # 入库前强制四舍五入
        if self.rating:
            self.rating = round(float(self.rating), 1)
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'movies'
        ordering = ['-rating', '-release_date']

    def __str__(self):
        return self.title


class Episode(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='episodes')
    season = models.IntegerField(default=1, verbose_name='季数')
    episode_number = models.IntegerField(verbose_name='集数')
    title = models.CharField(max_length=200, blank=True, verbose_name='标题')
    description = models.TextField(blank=True, verbose_name='简介')
    duration = models.IntegerField(null=True, blank=True, verbose_name='时长')
    air_date = models.DateField(null=True, blank=True, verbose_name='播出日期')
    still_url = models.URLField(max_length=500, blank=True, verbose_name='剧照')

    class Meta:
        db_table = 'episodes'  # 修改这里，原来是 'movies'
        ordering = ['season', 'episode_number']  # 修改这里，去掉 rating 和 release_date
        unique_together = ['movie', 'season', 'episode_number']


