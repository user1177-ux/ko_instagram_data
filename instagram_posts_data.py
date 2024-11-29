import csv
from datetime import datetime, timedelta
import requests

# Токен доступа и ID Instagram-аккаунта
access_token = 'EAAUjRaaBokMBOwfYtk6tknzsZCkDEy0qZAZBIdOzZA6V3uZCJyZBBRONZCEpzBbqI56kHFTewJS1jYFh8GF5PbUNKkGcytEZCxmFWjhZA0fsVuSI0O5qhfe3GH3nFMavvYCP41baTZCcSbNR2bmjCbAQxk9iHKppD1ClaqT9pTB8cXbpevzXGduQmTRldWDsfO2HfI6QjUdLaZCjZBFZAk5C0SgZDZD'
instagram_account_id = '17841459665084773'

# URL для запроса первой страницы медиа-объектов
base_url = f'https://graph.facebook.com/v20.0/{instagram_account_id}/media?fields=id,media_type,timestamp,like_count,comments_count,permalink,insights.metric(impressions,reach)&access_token={access_token}'

# Словарь для хранения данных
posts_data = {}
earliest_date = None  # Переменная для самой ранней даты публикации

# Функция для преобразования типа контента
def transform_media_type(media_type):
    if media_type == 'IMAGE':
        return 'пост'
    elif media_type == 'VIDEO':
        return 'рилс'
    elif media_type == 'CAROUSEL_ALBUM':
        return 'карусель'
    return 'неизвестно'

# Функция для получения дополнительных метрик рилсов
def get_reels_metrics(media_id):
    url = f'https://graph.facebook.com/v20.0/{media_id}/insights?metric=plays,video_views,ig_reels_aggregated_all_plays_count,ig_reels_avg_watch_time&period=lifetime&access_token={access_token}'
    response = requests.get(url)
    data = response.json()

    # Лог для проверки данных
    print(f"Ответ метрик для рилса {media_id}: {data}")

    metrics = {
        'plays': None,
        'video_views': None,
        'all_plays_count': None,
        'avg_watch_time': None
    }

    # Извлекаем значения метрик
    for item in data.get('data', []):
        if item['name'] == 'plays':
            metrics['plays'] = item['values'][0]['value']
        elif item['name'] == 'video_views':
            metrics['video_views'] = item['values'][0]['value']
        elif item['name'] == 'ig_reels_aggregated_all_plays_count':
            metrics['all_plays_count'] = item['values'][0]['value']
        elif item['name'] == 'ig_reels_avg_watch_time':
            metrics['avg_watch_time'] = item['values'][0]['value']

    return metrics

# Функция для обработки данных со страницы
def process_page(data):
    global earliest_date
    for media in data.get('data', []):
        media_id = media['id']
        media_type = transform_media_type(media.get('media_type', ''))  # Преобразуем тип
        date_str = media['timestamp'][:10]  # Извлекаем дату (YYYY-MM-DD)

        # Определяем самую раннюю дату
        if earliest_date is None or date_str < earliest_date:
            earliest_date = date_str

        # Инициализация данных для текущей даты
        if date_str not in posts_data:
            posts_data[date_str] = []

        # Получаем базовые метрики
        likes = media.get('like_count', 0)
        comments = media.get('comments_count', 0)
        permalink = media.get('permalink', '')

        # Если это рилс, запрашиваем дополнительные метрики
        reels_metrics = {}
        if media_type == 'рилс':
            reels_metrics = get_reels_metrics(media_id)

        # Добавляем данные по посту
        posts_data[date_str].append({
            'media_type': media_type,
            'likes': likes,
            'comments': comments,
            'permalink': permalink,
            'plays': reels_metrics.get('plays'),
            'video_views': reels_metrics.get('video_views'),
            'all_plays_count': reels_metrics.get('all_plays_count'),
            'avg_watch_time': reels_metrics.get('avg_watch_time')
        })

# Обрабатываем все страницы
next_url = base_url
while next_url:
    response = requests.get(next_url)
    data = response.json()

    # Лог для проверки текущей страницы
    print("Ответ API для страницы:", data)

    # Обрабатываем текущую страницу данных
    process_page(data)

    # Переходим на следующую страницу, если она есть
    next_url = data.get('paging', {}).get('next')

# Создаём полный список дат начиная с earliest_date до сегодняшнего дня
if earliest_date:
    start_date = datetime.strptime(earliest_date, '%Y-%m-%d')
    end_date = datetime.now()
    all_dates = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range((end_date - start_date).days + 1)]

    # Убедимся, что для всех дат есть данные
    for date in all_dates:
        if date not in posts_data:
            posts_data[date] = []

    # Сохраняем результаты в CSV файл
    with open('instagram_posts_data.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Дата', 'Тип поста', 'Лайки', 'Комментарии', 'Ссылка', 'Первичные воспроизведения', 'Просмотры (3 секунды)', 'Всего воспроизведений', 'Среднее время просмотра (мс)'])
        for date in sorted(posts_data.keys()):
            for post in posts_data[date]:
                writer.writerow([
                    date,
                    post['media_type'],
                    post['likes'],
                    post['comments'],
                    post['permalink'],
                    post.get('plays'),
                    post.get('video_views'),
                    post.get('all_plays_count'),
                    post.get('avg_watch_time')
                ])

    print(f"Данные успешно сохранены в 'instagram_posts_data.csv'. Данные с {earliest_date} по {end_date.strftime('%Y-%m-%d')}.")
else:
    print("Нет данных для записи в файл.")
