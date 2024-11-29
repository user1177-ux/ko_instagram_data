import csv
from datetime import datetime, timedelta
import requests

# Токен доступа и ID Instagram-аккаунта
access_token = 'EAAUjRaaBokMBOwfYtk6tknzsZCkDEy0qZAZBIdOzZA6V3uZCJyZBBRONZCEpzBbqI56kHFTewJS1jYFh8GF5PbUNKkGcytEZCxmFWjhZA0fsVuSI0O5qhfe3GH3nFMavvYCP41baTZCcSbNR2bmjCbAQxk9iHKppD1ClaqT9pTB8cXbpevzXGduQmTRldWDsfO2HfI6QjUdLaZCjZBFZAk5C0SgZDZD'
instagram_account_id = '17841459665084773'

# URL для запроса первой страницы медиа-объектов
base_url = f'https://graph.facebook.com/v20.0/{instagram_account_id}/media?fields=id,media_type,timestamp,like_count,comments_count,saved_count,shared_count,insights.metric(impressions)&access_token={access_token}'

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

# Функция для генерации ссылки на пост
def generate_post_link(media_id):
    return f"https://www.instagram.com/p/{media_id}/"

# Функция для обработки данных со страницы
def process_page(data):
    global earliest_date
    for media in data.get('data', []):
        print("Медиа объект:", media)  # Отладочный вывод для проверки данных

        media_id = media['id']
        media_type = transform_media_type(media.get('media_type', ''))  # Преобразуем тип
        date_str = media['timestamp'][:10]  # Извлекаем дату (YYYY-MM-DD)

        # Определяем самую раннюю дату
        if earliest_date is None or date_str < earliest_date:
            earliest_date = date_str

        # Инициализация данных для текущей даты
        if date_str not in posts_data:
            posts_data[date_str] = []

        # Получаем метрики из объекта
        views = 0
        insights = media.get('insights', {}).get('data', [])
        for metric in insights:
            if metric['name'] == 'impressions':
                views = metric.get('values', [{}])[0].get('value', 0)

        # Добавляем данные по посту
        posts_data[date_str].append({
            'media_type': media_type,
            'views': views,
            'likes': media.get('like_count', 0),
            'comments': media.get('comments_count', 0),
            'shares': media.get('shared_count', 0),
            'saves': media.get('saved_count', 0),
            'link': generate_post_link(media_id)
        })

# Обрабатываем все страницы
next_url = base_url
while next_url:
    response = requests.get(next_url)
    data = response.json()

    print("Ответ API для страницы:", data)  # Лог для проверки страницы

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
    print("Итоговые данные для CSV:", posts_data)  # Лог перед записью в файл
    with open('instagram_posts_data.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Дата', 'Тип поста', 'Просмотры', 'Лайки', 'Комментарии', 'Репосты', 'Сохранения', 'Ссылка'])
        for date in sorted(posts_data.keys()):
            for post in posts_data[date]:
                writer.writerow([date, post['media_type'], post['views'], post['likes'], post['comments'], post['shares'], post['saves'], post['link']])

    print(f"Данные успешно сохранены в 'instagram_posts_data.csv'. Данные с {earliest_date} по {end_date.strftime('%Y-%m-%d')}.")
else:
    print("Нет данных для записи в файл.")
