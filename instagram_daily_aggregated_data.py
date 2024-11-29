import csv
from datetime import datetime, timedelta
import requests

# Токен доступа и ID Instagram-аккаунта
access_token = 'EAAUjRaaBokMBOxBXe4jGKE9cfhz1nOOiZB83gr5U0lEAna3v99SCZAuW6CtooONvAbnQBTB1EBx6GsJ7e4ZBcFGRN6Fb6eJ29qx3YUf1rql72B3tGehsSy0egmZCcFQwS36dSLpPXCqMvEzNauCjZCZAttTZBBsbo9zDZCoX2oWJavUyB3EWMnJGBC1s'
instagram_account_id = '17841459665084773'

# URL для запроса первой страницы медиа-объектов
base_url = f'https://graph.facebook.com/v20.0/{instagram_account_id}/media?fields=id,media_type,timestamp,like_count,comments_count,saved_count,shared_count,insights.metric(impressions,plays)&access_token={access_token}'

# Словарь для хранения данных
daily_data = {}
earliest_date = None

# Функция для обработки данных со страницы
def process_page(data):
    global earliest_date
    for media in data.get('data', []):
        timestamp = media['timestamp'][:10]  # Дата публикации (YYYY-MM-DD)
        media_type = media.get('media_type', '')
        likes = media.get('like_count', 0)
        comments = media.get('comments_count', 0)
        saves = media.get('saved_count', 0)
        shares = media.get('shared_count', 0)
        impressions = 0  # Для просмотров постов
        plays = 0  # Для просмотров рилс

        # Проверяем и обновляем самую раннюю дату
        if earliest_date is None or timestamp < earliest_date:
            earliest_date = timestamp

        # Извлекаем метрики "impressions" и "plays"
        insights = media.get('insights', {}).get('data', [])
        for metric in insights:
            if metric['name'] == 'impressions':
                impressions = metric['values'][0]['value']
            elif metric['name'] == 'plays':
                plays = metric['values'][0]['value']

        # Агрегируем метрики по дате
        if timestamp not in daily_data:
            daily_data[timestamp] = {
                'likes': 0,
                'comments': 0,
                'saves': 0,
                'shares': 0,
                'post_views': 0,
                'reels_views': 0
            }

        daily_data[timestamp]['likes'] += likes
        daily_data[timestamp]['comments'] += comments
        daily_data[timestamp]['saves'] += saves
        daily_data[timestamp]['shares'] += shares

        if media_type in ['IMAGE', 'CAROUSEL_ALBUM', 'VIDEO']:  # Для постов
            daily_data[timestamp]['post_views'] += impressions
        elif media_type == 'REELS':  # Для рилс
            daily_data[timestamp]['reels_views'] += plays

# Обрабатываем все страницы
next_url = base_url
while next_url:
    response = requests.get(next_url)
    data = response.json()

    # Лог для проверки данных
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
        if date not in daily_data:
            daily_data[date] = {'likes': 0, 'comments': 0, 'saves': 0, 'shares': 0, 'post_views': 0, 'reels_views': 0}

    # Сохраняем результаты в CSV файл
    with open('instagram_daily_aggregated_data.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Дата', 'Лайки', 'Просмотры постов', 'Просмотры рилс', 'Комментарии', 'Репосты', 'Сохранения'])
        for date in sorted(daily_data.keys()):
            metrics = daily_data[date]
            writer.writerow([
                date,
                metrics['likes'],
                metrics['post_views'],  # Просмотры постов
                metrics['reels_views'],  # Просмотры рилс
                metrics['comments'],
                metrics['shares'],
                metrics['saves']
            ])

    print(f"Данные успешно сохранены в 'instagram_daily_aggregated_data.csv'. Данные с {earliest_date} по {end_date.strftime('%Y-%m-%d')}.")
else:
    print("Нет данных для записи в файл.")
