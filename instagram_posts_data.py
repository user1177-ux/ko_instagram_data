import csv
from datetime import datetime, timedelta
import requests

# Токен доступа и ID Instagram-аккаунта
access_token = 'EAAUjRaaBokMBO9exzG388hsSSw1RfCZCHWrrQ4KBzULi1fTjwNJ3Hm34rWVIPfjKeBQ5k12A6uAsUjqtb1i2YMi1PySuXhbwOJQjRznLOmzNe0eBW538zOhCVFBCFrvIEVi5ZAbKxrOnQORAD0LZBBJuhObXvVxk4E6OZBHeCIemyXpxJBk30ZA4Q'
instagram_account_id = '17841459665084773'

# Проверка, что переменные окружения заданы
if not access_token or not instagram_account_id:
    raise ValueError("Токен доступа или ID аккаунта не установлены.")

# URL для запроса первой страницы медиа-объектов
base_url = f'https://graph.facebook.com/v20.0/{instagram_account_id}/media?fields=id,timestamp&access_token={access_token}'

# Словарь для хранения публикаций, лайков и комментариев по датам
posts_data = {}
earliest_date = None  # Переменная для самой ранней даты публикации

# Функция для обработки данных со страницы
def process_page(data):
    global earliest_date
    for media in data.get('data', []):
        media_id = media['id']
        date_str = media['timestamp'][:10]  # Извлекаем дату (YYYY-MM-DD)

        # Определяем самую раннюю дату
        if earliest_date is None or date_str < earliest_date:
            earliest_date = date_str

        # Запрашиваем лайки и комментарии для конкретного поста
        metrics_url = f'https://graph.facebook.com/v20.0/{media_id}?fields=like_count,comments_count&access_token={access_token}'
        metrics_response = requests.get(metrics_url)
        metrics_data = metrics_response.json()

        # Инициализация данных для текущей даты
        if date_str not in posts_data:
            posts_data[date_str] = {'posts_count': 0, 'likes': 0, 'comments': 0}

        # Увеличиваем количество публикаций
        posts_data[date_str]['posts_count'] += 1

        # Добавляем лайки и комментарии
        posts_data[date_str]['likes'] += metrics_data.get('like_count', 0)
        posts_data[date_str]['comments'] += metrics_data.get('comments_count', 0)

# Обрабатываем все страницы
next_url = base_url
while next_url:
    response = requests.get(next_url)
    data = response.json()

    # Обрабатываем текущую страницу данных
    process_page(data)

    # Переходим на следующую страницу, если она есть
    next_url = data.get('paging', {}).get('next')

# Создаём полный список дат начиная с earliest_date до сегодняшнего дня
if earliest_date:
    start_date = datetime.strptime(earliest_date, '%Y-%m-%d')
    end_date = datetime.now()
    all_dates = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range((end_date - start_date).days + 1)]

    # Убедимся, что для всех дат есть данные (добавляем 0 для отсутствующих дат)
    for date in all_dates:
        if date not in posts_data:
            posts_data[date] = {'posts_count': 0, 'likes': 0, 'comments': 0}

    # Сохраняем результаты в CSV файл
    with open('instagram_posts_data.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Дата', 'Количество публикаций', 'Лайки', 'Комментарии'])
        for date in sorted(posts_data.keys()):
            metrics = posts_data[date]
            writer.writerow([date, metrics['posts_count'], metrics['likes'], metrics['comments']])

    print(f"Данные успешно сохранены в 'instagram_posts_data.csv'. Данные с {earliest_date} по {end_date.strftime('%Y-%m-%d')}.")
else:
    print("Нет данных для записи в файл.")
