# 保存为 export_movies.py，放在 backend 目录下
import os
import sys
import json

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

from django.core.serializers import serialize
from apps.movies.models import Movie, Genre

# 序列化数据
movies_json = serialize('json', Movie.objects.all())
genres_json = serialize('json', Genre.objects.all())

# 合并
movies_data = json.loads(movies_json)
genres_data = json.loads(genres_json)
all_data = movies_data + genres_data

# 直接写入 UTF-8 文件（无 BOM）
output_path = os.path.join(os.path.dirname(__file__), 'movies_export.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

print(f'导出完成: {output_path}')
print(f'电影: {len(movies_data)} 部')
print(f'类型: {len(genres_data)} 个')
print(f'总计: {len(all_data)} 条记录')
