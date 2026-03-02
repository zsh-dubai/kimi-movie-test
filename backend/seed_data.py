import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.movies.models import Movie, Genre
from apps.users.models import User


def create_test_data():
    # 创建类型
    genres_data = ['动作', '喜剧', '剧情', '科幻', '恐怖', '爱情', '动画', '悬疑', '犯罪', '传记', '历史', '奇幻', '运动']

    genres = {}
    for name in genres_data:
        genre, _ = Genre.objects.get_or_create(name=name)
        genres[name] = genre

    # 创建测试影视数据
    movies_data = [
        {
            'title': '流浪地球2',
            'original_title': 'The Wandering Earth II',
            'description': '太阳即将毁灭，人类在地球表面建造出巨大的推进器，寻找新的家园。然而宇宙之路危机四伏，为了拯救地球，流浪地球时代的年轻人再次挺身而出，展开争分夺秒的生死之战。',
            'movie_type': 'movie',
            'genres': ['科幻', '动作', '剧情'],
            'release_date': '2023-01-22',
            'duration': 173,
            'rating': 8.3,
            'rating_count': 1500000,
            'director': '郭帆',
            'cast': ['吴京', '刘德华', '李雪健', '沙溢'],
            'poster_url': 'https://img9.doubanio.com/view/photo/s_ratio_poster/public/p2885842436.jpg',
            'backdrop_url': 'https://img9.doubanio.com/view/photo/s_ratio_poster/public/p2885842436.jpg',
        },
        {
            'title': '狂飙',
            'original_title': '',
            'description': '京海市一线刑警安欣，在与黑恶势力的斗争中，不断遭到保护伞的打击，始终无法将犯罪分子绳之以法。全国政法队伍教育整顿工作开展后，临江省派出指导组入驻京海，联合公检法司各部门，清除了政法队伍内部的腐败分子，粉碎了黑恶势力的保护伞，一举铲除了盘踞京海多年的强盛集团。',
            'movie_type': 'tv',
            'genres': ['剧情', '犯罪', '悬疑'],
            'release_date': '2023-01-14',
            'duration': 45,
            'rating': 8.5,
            'rating_count': 800000,
            'director': '徐纪周',
            'cast': ['张译', '张颂文', '李一桐', '张志坚'],
            'poster_url': 'https://img9.doubanio.com/view/photo/s_ratio_poster/public/p2886376181.jpg',
            'backdrop_url': 'https://img9.doubanio.com/view/photo/s_ratio_poster/public/p2886376181.jpg',
        },
        {
            'title': '铃芽之旅',
            'original_title': 'すずめの戸締まり',
            'description': '宁静的九州乡间小镇，生活着平凡的少女岩户铃芽。这天上学路上，她邂逅了神秘的白衣青年宗像草太。草太的言行举止引起了铃芽的好奇，她跟随草太进入废墟，发现了一扇通往异世界的大门。',
            'movie_type': 'anime',
            'genres': ['动画', '爱情', '奇幻'],
            'release_date': '2023-03-24',
            'duration': 122,
            'rating': 7.9,
            'rating_count': 600000,
            'director': '新海诚',
            'cast': ['原菜乃华', '松村北斗', '深津绘里'],
            'poster_url': 'https://img9.doubanio.com/view/photo/s_ratio_poster/public/p2888398295.jpg',
            'backdrop_url': 'https://img9.doubanio.com/view/photo/s_ratio_poster/public/p2888398295.jpg',
        },
        {
            'title': '奥本海默',
            'original_title': 'Oppenheimer',
            'description': '影片聚焦"原子弹之父"罗伯特·奥本海默的一生，讲述了美国理论物理学家罗伯特·奥本海默主导研制世界上第一颗原子弹的过程。',
            'movie_type': 'movie',
            'genres': ['剧情', '传记', '历史'],
            'release_date': '2023-08-30',
            'duration': 180,
            'rating': 8.8,
            'rating_count': 450000,
            'director': '克里斯托弗·诺兰',
            'cast': ['基里安·墨菲', '艾米莉·布朗特', '马特·达蒙'],
            'poster_url': 'https://img9.doubanio.com/view/photo/s_ratio_poster/public/p2896558452.jpg',
            'backdrop_url': 'https://img9.doubanio.com/view/photo/s_ratio_poster/public/p2896558452.jpg',
        },
        {
            'title': '漫长的季节',
            'original_title': '',
            'description': '小城桦林，此时，出租司机王响梦想着一夜暴富，开火车之余也开出租。王响的妹夫龚彪，当年也是厂里的天之骄子，如今却沦落到开出租。王响的独子王阳，高考失利，前途未卜。',
            'movie_type': 'tv',
            'genres': ['剧情', '犯罪', '悬疑'],
            'release_date': '2023-04-22',
            'duration': 60,
            'rating': 9.4,
            'rating_count': 500000,
            'director': '辛爽',
            'cast': ['范伟', '秦昊', '陈明昊', '李庚希'],
            'poster_url': 'https://img9.doubanio.com/view/photo/s_ratio_poster/public/p2890906381.jpg',
            'backdrop_url': 'https://img9.doubanio.com/view/photo/s_ratio_poster/public/p2890906381.jpg',
        },
        {
            'title': '灌篮高手',
            'original_title': 'THE FIRST SLAM DUNK',
            'description': '宫城良田、三井寿、流川枫、樱木花道和赤木刚宪终于站在全国大赛的赛场，代表湘北高中与日本最强球队山王工业展开激烈对决。',
            'movie_type': 'anime',
            'genres': ['动画', '运动'],
            'release_date': '2023-04-20',
            'duration': 124,
            'rating': 8.9,
            'rating_count': 400000,
            'director': '井上雄彦',
            'cast': ['仲村宗悟', '笠间淳', '木村昴'],
            'poster_url': 'https://img9.doubanio.com/view/photo/s_ratio_poster/public/p2888398295.jpg',
            'backdrop_url': 'https://img9.doubanio.com/view/photo/s_ratio_poster/public/p2888398295.jpg',
        },
    ]

    for movie_data in movies_data:
        genre_names = movie_data.pop('genres')
        movie, created = Movie.objects.get_or_create(
            title=movie_data['title'],
            defaults=movie_data
        )
        if created:
            for genre_name in genre_names:
                movie.genres.add(genres[genre_name])
            print(f"创建: {movie.title}")
        else:
            print(f"已存在: {movie.title}")

    print("\n测试数据创建完成！")


if __name__ == '__main__':
    create_test_data()
