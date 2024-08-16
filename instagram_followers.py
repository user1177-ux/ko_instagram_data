import requests
import datetime
import csv
import os

# Ваш токен доступа
access_token = 'ACCESS_TOKEN'
# ID вашего бизнес-аккаунта Instagram
instagram_account_id = 'INSTAGRAM_ACCOUNT_ID'

# Конечная точка API для получения количества подписчиков
url = f'https://graph.facebook.com/v12.0/{instagram_account_id}/insights'

# Запрашиваемые параметры
params = {
    'metric': 'follower_count',
    'period': 'day',
    'access_token': access_token
}

# Получаем текущую дату и дату два месяца назад
end_date = datetime.datetime.now().date()
start_date = (end_date - datetime.timedelta(days=60)).strftime('%Y-%m-%d')

# Добавляем временной интервал в параметры запроса
params['since'] = start_date
params['until'] = end_date.strftime('%Y-%m-%d')

# Отправляем запрос к API
response = requests.get(url, params=params)
data = response.json()

# Печатаем полный ответ API для диагностики
print("API response:", data)

# Проверяем, есть ли данные в ответе
if 'data' in data:
    print("Data found, proceeding to create file.")
    # Сохраняем данные в CSV файл
    with open('instagram_followers.csv', 'w', newline='') as csvfile:
        fieldnames = ['date', 'followers_count']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for entry in data['data'][0]['values']:
            writer.writerow({'date': entry['end_time'], 'followers_count': entry['value']})

    print("File 'instagram_followers.csv' created successfully in:", os.getcwd())
else:
    print("No 'data' key found in API response. Response received:")
    print(data)
