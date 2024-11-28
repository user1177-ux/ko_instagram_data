import csv
from datetime import datetime, timedelta
import requests

# Токен доступа и ID Instagram-аккаунта
access_token = 'EAAUjRaaBokMBOZB8hVrQwvF9jMnbiePwFBWbjpW5WZBY8c6uZCzwjxqcO3nxGxKhtCPJhVPtxyv6TyhsUiMfX8SxJk3RwRIsmqbiUSDviWWbZBXRYbcXUSdtShkBNkwJ82Vc8bHqT0KXTbHsZAjDESKUGv9Ci5bfZBn8Mj7l2WZBbyECSpyPmoQZAeMc3aZAkzvqzwd0V7k4a8E6PaxCeVwZDZD'
instagram_account_id = '17841459665084773'

# Проверка, что переменные окружения заданы
if not access_token or not instagram_account_id:
    raise ValueError("Токен доступа или ID аккаунта не установлены.")

# URL для запроса первой страницы медиа-объектов
base_url = f'https://graph.facebook.com/v20.0/{instagram_account_id}/media?fields=id,media_type,timestamp,caption&access_token={access_token}'

# Словарь для хранения данных
posts_data = {}
earliest_date = None  # Переменная для самой ранней даты публикации

# Функция для обработки данных со страницы
def process_page(data):
    global earliest_date
    for media in data.get('data', []):
        print("Медиа объект:", media)  # Лог для отладки данных от API

        media_id = media['id']
        media_type = media.get('media_type', '')  # Тип медиа
        date_str = media['timestamp'][:10]  # Извлекаем дату (YYYY-MM-DD)

        # Определяем самую раннюю дату
        if earliest_date is None or date_str < earliest_date:
            earliest_date = date_str

        # Инициализация данных для текущей даты
        if date_str not in posts_data:
            posts_data[date_str] = {'posts_count': 0, 'carousel_count': 0, 'reels_count': 0,
                                    'likes': 0, 'comments': 0, 'saves': 0, 'shares': 0, 'views': 0}

        # Разделяем на посты, карусели и рилсы
        if media_type == 'VIDEO':  # Рилсы
            print(f"Определён как рилс: {media}")
            posts_data[date_str]['reels_count'] += 1
        elif media_type == 'CAROUSEL_ALBUM':  # Карусели
            print(f"Определён как карусель: {media}")
            posts_data[date_str]['carousel_count'] += 1
        elif media_type == 'IMAGE':  # Посты
            print(f"Определён как пост: {media}")
            posts_data[date_str]['posts_count'] += 1

        # Запрашиваем дополнительные метрики для конкретного поста
        metrics_url = f'https://graph.facebook.com/v20.0/{media_id}?fields=like_count,comments_count,saved_count,shared_count,insights.metric(impressions)&access_token={access_token}'
        metrics_response = requests.get(metrics_url)
        metrics_data = metrics_response.json()

        # Добавляем лайки, комментарии, сохранения, репосты и просмотры
        posts_data[date_str]['likes'] += metrics_data.get('like_count', 0)
        posts_data[date_str]['comments'] += metrics_data.get('comments_count', 0)
        posts_data[date_str]['saves'] += metrics_data.get('saved_count', 0)
        posts_data[date_str]['shares'] += metrics_data.get('shared_count', 0)
        # Просмотры приходят в метрике insights
        insights = metrics_data.get('insights', {}).get('data', [])
        for metric in insights:
            if metric['name'] == 'impressions':
                posts_data[date_str]['views'] += metric.get('values', [{}])[0].get('value', 0)

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

    # Убедимся, что для всех дат есть данные (добавляем 0 для отсутствующих дат)
    for date in all_dates:
        if date not in posts_data:
            posts_data[date] = {'posts_count': 0, 'carousel_count': 0, 'reels_count': 0,
                                'likes': 0, 'comments': 0, 'saves': 0, 'shares': 0, 'views': 0}

    # Сохраняем результаты в CSV файл
    print("Итоговые данные для CSV:", posts_data)  # Лог перед записью в файл
    with open('instagram_posts_data.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Дата', 'Посты', 'Карусели', 'Рилсы', 'Лайки', 'Комментарии', 'Сохранения', 'Репосты', 'Просмотры'])
        for date in sorted(posts_data.keys()):
            metrics = posts_data[date]
            writer.writerow([date, metrics['posts_count'], metrics['carousel_count'], metrics['reels_count'],
                             metrics['likes'], metrics['comments'], metrics['saves'], metrics['shares'], metrics['views']])

    print(f"Данные успешно сохранены в 'instagram_posts_data.csv'. Данные с {earliest_date} по {end_date.strftime('%Y-%m-%d')}.")
else:
    print("Нет данных для записи в файл.")
