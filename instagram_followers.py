import requests
import csv
from datetime import datetime

# Замените на ваш access_token и instagram_account_id
access_token = 'ВАШ_ТОКЕН_ДОСТУПА'
instagram_account_id = 'ВАШ_ИНСТАГРАМ_АККАУНТ_ID'

# URL для запроса медиа-объектов аккаунта
url = f'https://graph.facebook.com/v20.0/{instagram_account_id}/media?fields=id,timestamp&access_token={access_token}'

# Запрашиваем данные о публикациях
response = requests.get(url)
data = response.json()

# Инициализируем словарь для хранения количества публикаций по датам
posts_by_date = {}

# Обрабатываем полученные данные
while True:
    for media in data['data']:
        # Получаем дату публикации в формате YYYY-MM-DD
        date = media['timestamp'][:10]

        # Увеличиваем счетчик публикаций для этой даты
        if date in posts_by_date:
            posts_by_date[date] += 1
        else:
            posts_by_date[date] = 1

    # Проверяем, есть ли следующая страница с данными
    if 'paging' in data and 'next' in data['paging']:
        next_url = data['paging']['next']
        response = requests.get(next_url)
        data = response.json()
    else:
        break

# Сортируем даты
sorted_dates = sorted(posts_by_date.keys())

# Путь для сохранения CSV файла
csv_file_path = 'instagram_posts_data.csv'

# Записываем данные в CSV
with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Дата', 'Количество публикаций'])

    for date in sorted_dates:
        writer.writerow([date, posts_by_date[date]])

print(f'Data saved to {csv_file_path}')
