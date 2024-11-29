import csv
from datetime import datetime, timedelta
import requests

# Токен доступа и ID Instagram-аккаунта
access_token = 'EAAUjRaaBokMBOzgZAYEtvLIvkWnC2PVlH6AbRMMY6BNVyqVXWRZA4llHvWa0mCM3qACEJGuCfeJSsH83jqCRMhS4Ur9jqTxuMTD5RTNUQmmg7pQYaNErBZBK8NY41l7A1506llWdcUdxjSaChUTVLoV9qiJhd115SFZBcL8PXlWceJgRhJvZBeZCfJkejAN3rCXxwbA74ZCzocuws0etYAZD'
instagram_account_id = '17841459665084773'

# URL для запроса медиа-объектов
base_url = f'https://graph.facebook.com/v20.0/{instagram_account_id}/media?fields=id,media_type,timestamp,like_count,comments_count,permalink,insights.metric(plays)&access_token={access_token}'

# Список для хранения данных
reels_data = []

# Функция для обработки страницы
def process_page(data):
    for media in data.get('data', []):
        if media.get('media_type') == 'VIDEO':  # Фильтруем только рилсы
            media_id = media['id']
            timestamp = media['timestamp'][:10]  # Дата публикации (YYYY-MM-DD)
            permalink = media.get('permalink', '1')  # Ссылка на рилс или "1", если недоступна
            like_count = media.get('like_count', 0)
            comments_count = media.get('comments_count', 0)

            # Запрашиваем количество просмотров
            plays = None
            insights_url = f'https://graph.facebook.com/v20.0/{media_id}/insights?metric=plays&period=lifetime&access_token={access_token}'
            insights_response = requests.get(insights_url)
            insights_data = insights_response.json()

            for metric in insights_data.get('data', []):
                if metric['name'] == 'plays':
                    plays = metric['values'][0]['value']

            # Добавляем данные в список
            reels_data.append({
                'date': timestamp,
                'permalink': permalink,
                'plays': plays,
                'likes': like_count,
                'comments': comments_count
            })

# Обрабатываем все страницы
next_url = base_url
while next_url:
    response = requests.get(next_url)
    data = response.json()

    # Лог для проверки данных
    print("Ответ API для страницы:", data)

    # Обрабатываем текущую страницу
    process_page(data)

    # Переходим на следующую страницу, если она есть
    next_url = data.get('paging', {}).get('next')

# Сортируем данные по дате публикации
reels_data.sort(key=lambda x: x['date'])

# Сохраняем результаты в CSV
with open('instagram_reels_data.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Дата публикации', 'Ссылка на рилс', 'Кол-во просмотров', 'Кол-во реакций', 'Кол-во комментариев'])
    for reel in reels_data:
        writer.writerow([
            reel['date'],
            reel['permalink'],
            reel['plays'],
            reel['likes'],
            reel['comments']
        ])

print(f"Данные успешно сохранены в 'instagram_reels_data.csv'. Исторические данные собраны.")
