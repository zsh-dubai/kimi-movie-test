from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('apps.users.urls')),
    path('api/movies/', include('apps.movies.urls')),
    path('api/recommendations/', include('apps.recommendations.urls')),
    path('api/interactions/', include('apps.interactions.urls')),
    path('', TemplateView.as_view(template_name='index.html')),  # 添加首页
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
