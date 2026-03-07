from django.contrib import admin
from .models import Movie, Genre


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'rating', 'release_date', 'movie_type', 'play_url']  # 列表页显示的字段
    list_editable = ['play_url']  # 直接在列表页编辑
    list_filter = ['movie_type', 'genres', 'release_date']  # 右侧筛选器
    search_fields = ['title', 'original_title']  # 搜索框

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'tmdb_id']
    search_fields = ['name']
