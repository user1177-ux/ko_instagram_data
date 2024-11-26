import requests
import csv
from datetime import datetime

# Замените на ваш access_token и instagram_account_id
access_token = 'EAAUjRaaBokMBO02Q6CVeAjWLBdchyobrh8Ogd6vudHpcM06BjJ96RnnfJmVi9aafWZBLnEsllDZAh4jeIWK9iVDBbdNN2YXl6dEZAjWNMKcrBiNa0HivjhuGvPEIKTXRPoOFvjLvPqdcVCdkAsikiMaVaqWco3oxYkMiDsVdS6xj9R0vuHuJOgq1QVINbiWIFl7UI3AMhqhTFcKMBudOjdWMLYZD'
instagram_account_id = '17841459665084773'

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
    # Создаем словарь для подсчета количества публикаций по датам
    posts_per_date = {}

    # Проходим по всем медиа-объектам и считаем публикации по датам
    for media in data['data']:
        date_str = media['timestamp'][:10]  # Извлекаем дату (YYYY-MM-DD)
        if date_str in posts_per_date:
            posts_per_date[date_str] += 1
        else:
            posts_per_date[date_str] = 1

    # Проверяем, есть ли данные для сохранения
    if posts_per_date:
        # Сохраняем результаты в CSV файл
        with open('instagram_posts_data.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Дата', 'Количество публикаций'])
            for date, count in sorted(posts_per_date.items()):
                writer.writerow([date, count])

        print("Данные успешно сохранены в 'instagram_posts_data.csv'.")
    else:
        print("Нет данных для записи в файл.")

# Убедитесь, что скрипт завершился успешно
exit(0)
