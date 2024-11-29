import csv
from datetime import datetime, timedelta
import requests

# Токен доступа и ID Instagram-аккаунта
access_token = 'EAAUjRaaBokMBOzgZAYEtvLIvkWnC2PVlH6AbRMMY6BNVyqVXWRZA4llHvWa0mCM3qACEJGuCfeJSsH83jqCRMhS4Ur9jqTxuMTD5RTNUQmmg7pQYaNErBZBK8NY41l7A1506llWdcUdxjSaChUTVLoV9qiJhd115SFZBcL8PXlWceJgRhJvZBeZCfJkejAN3rCXxwbA74ZCzocuws0etYAZD'
instagram_account_id = '17841459665084773'

# URL для запроса медиа-объектов
base_url = f'https://graph.facebook.com/v20.0/{instagram_account_id}/stories?fields=id,timestamp,permalink,insights.metric(impressions,reach,replies)&access_token={access_token}'

# Список для хранения данных
stories_data = []

# Функция для обработки страницы
def process_page(data):
    for story in data.get('data', []):
        story_id = story['id']
        timestamp = story['timestamp'][:10]  # Дата публикации (YYYY-MM-DD)
        permalink = story.get('permalink', '1')  # Ссылка на сторис или "1", если недоступна

        # Инициализация метрик
        impressions = None
        reach = None
        replies = None

        # Запрашиваем метрики
        insights_url = f'https://graph.facebook.com/v20.0/{story_id}/insights?metric=impressions,reach,replies&period=lifetime&access_token={access_token}'
        insights_response = requests.get(insights_url)
        insights_data = insights_response.json()

        # Извлекаем метрики из ответа
        for metric in insights_data.get('data', []):
            if metric['name'] == 'impressions':
                impressions = metric['values'][0]['value']
            elif metric['name'] == 'reach':
                reach = metric['values'][0]['value']
            elif metric['name'] == 'replies':
                replies = metric['values'][0]['value']

        # Добавляем данные в список
        stories_data.append({
            'date': timestamp,
            'permalink': permalink,
            'impressions': impressions,
            'reach': reach,
            'replies': replies
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
stories_data.sort(key=lambda x: x['date'])

# Сохраняем результаты в CSV
with open('instagram_stories_data.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Дата публикации', 'Ссылка на сторис', 'Кол-во просмотров', 'Охват', 'Ответы'])
    for story in stories_data:
        writer.writerow([
            story['date'],
            story['permalink'],
            story['impressions'],
            story['reach'],
            story['replies']
        ])

print(f"Данные успешно сохранены в 'instagram_stories_data.csv'. Исторические данные собраны.")
