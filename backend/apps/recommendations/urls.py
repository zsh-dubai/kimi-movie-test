from django.urls import path
from . import views

urlpatterns = [
    path('for-you/', views.for_you, name='for_you'),
    path('trending/', views.trending_movies, name='trending'),
    path('similar/<int:movie_id>/', views.similar_movies, name='similar'),
]
