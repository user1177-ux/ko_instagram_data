import requests
import csv
from datetime import datetime

# Токен доступа и ID Instagram-аккаунта
access_token = 'EAAUjRaaBokMBO02Q6CVeAjWLBdchyobrh8Ogd6vudHpcM06BjJ96RnnfJmVi9aafWZBLnEsllDZAh4jeIWK9iVDBbdNN2YXl6dEZAjWNMKcrBiNa0HivjhuGvPEIKTXRPoOFvjLvPqdcVCdkAsikiMaVaqWco3oxYkMiDsVdS6xj9R0vuHuJOgq1QVINbiWIFl7UI3AMhqhTFcKMBudOjdWMLYZD'
instagram_account_id = '17841459665084773'

# Проверка, что переменные окружения заданы
if not access_token or not instagram_account_id:
    raise ValueError("Токен доступа (ACCESS_TOKEN) или ID аккаунта (INSTAGRAM_ACCOUNT_ID) не установлены.")

# URL для запроса медиа-объектов аккаунта
url = f'https://graph.facebook.com/v20.0/{instagram_account_id}/media?fields=id,timestamp&access_token={access_token}'

response = requests.get(url)
data = response.json()

# Вывод полного ответа API для отладки
print(data)

# Проверяем наличие ключа 'data' в ответе
if 'data' not in data:
    print("Ошибка: нет данных в ответе API.")
else:
    # Создаем словарь для подсчета публикаций, лайков и комментариев по датам
    posts_data = {}

    # Проходим по всем медиа-объектам
    for media in data['data']:
        media_id = media['id']
        date_str = media['timestamp'][:10]  # Извлекаем дату (YYYY-MM-DD)

        # Запрашиваем метрики для конкретного поста
        metrics_url = f'https://graph.facebook.com/v20.0/{media_id}/insights?metric=engagement,impressions,comments&access_token={access_token}'
        metrics_response = requests.get(metrics_url)
        metrics_data = metrics_response.json()

        # Инициализация данных для текущей даты
        if date_str not in posts_data:
            posts_data[date_str] = {'posts_count': 0, 'likes': 0, 'comments': 0}

        # Увеличиваем количество публикаций
        posts_data[date_str]['posts_count'] += 1

        # Добавляем лайки и комментарии из метрик
        for metric in metrics_data.get('data', []):
            if metric['name'] == 'engagement':
                posts_data[date_str]['likes'] += metric['values'][0]['value']
            elif metric['name'] == 'comments':
                posts_data[date_str]['comments'] += metric['values'][0]['value']

    # Проверяем, есть ли данные для сохранения
    if posts_data:
        # Сохраняем результаты в CSV файл
        with open('instagram_posts_data.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Дата', 'Количество публикаций', 'Лайки', 'Комментарии'])
            for date, metrics in sorted(posts_data.items()):
                writer.writerow([date, metrics['posts_count'], metrics['likes'], metrics['comments']])

        print("Данные успешно сохранены в 'instagram_posts_data.csv'.")
    else:
        print("Нет данных для записи в файл.")

# Убедитесь, что скрипт завершился успешно
exit(0)
