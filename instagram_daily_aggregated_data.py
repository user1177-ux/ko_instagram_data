import csv
from datetime import datetime, timedelta
import requests

# Токен доступа и ID Instagram-аккаунта
access_token = 'EAAUjRaaBokMBOxBXe4jGKE9cfhz1nOOiZB83gr5U0lEAna3v99SCZAuW6CtooONvAbnQBTB1EBx6GsJ7e4ZBcFGRN6Fb6eJ29qx3YUf1rql72B3tGehsSy0egmZCcFQwS36dSLpPXCqMvEzNauCjZCZAttTZBBsbo9zDZCoX2oWJavUyB3EWMnJGBC1s'
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
            posts_data[date_str] = {
                'likes': 0,
                'comments': 0,
                'saves': 0,
                'shares': 0,
                'impressions': 0  # Просмотры
            }

        # Получаем базовые метрики
        likes = media.get('like_count', 0)
        comments = media.get('comments_count', 0)
        saves = media.get('saved_count', 0)
        shares = media.get('shared_count', 0)
        impressions = 0

        # Получаем просмотры из insights, если они есть
        insights = media.get('insights', {}).get('data', [])
        for insight in insights:
            if insight['name'] == 'impressions':
                impressions = insight['values'][0]['value']

        # Агрегируем данные
        posts_data[date_str]['likes'] += likes
        posts_data[date_str]['comments'] += comments
        posts_data[date_str]['saves'] += saves
        posts_data[date_str]['shares'] += shares
        posts_data[date_str]['impressions'] += impressions

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
            posts_data[date] = {
                'likes': 0,
                'comments': 0,
                'saves': 0,
                'shares': 0,
                'impressions': 0
            }

    # Сохраняем результаты в CSV файл
    with open('instagram_daily_aggregated_data.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Дата', 'Лайки', 'Просмотры', 'Комментарии', 'Репосты', 'Сохранения'])
        for date in sorted(posts_data.keys()):
            metrics = posts_data[date]
            writer.writerow([
                date,
                metrics['likes'],
                metrics['impressions'],
                metrics['comments'],
                metrics['shares'],
                metrics['saves']
            ])

    print(f"Данные успешно сохранены в 'instagram_daily_aggregated_data.csv'. Данные с {earliest_date} по {end_date.strftime('%Y-%m-%d')}.")
else:
    print("Нет данных для записи в файл.")
