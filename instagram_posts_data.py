import requests
import csv
import os
import json
from datetime import datetime, timedelta

def fetch_data():
    access_token = os.getenv('ACCESS_TOKEN')
    ad_account_id = os.getenv('AD_ACCOUNT_ID')

    if not access_token or not ad_account_id:
        print("ACCESS_TOKEN or AD_ACCOUNT_ID not set")
        return

    # Даты
    end_date = datetime.now() - timedelta(days=1)
    end_date_str = end_date.strftime('%Y-%m-%d')
    start_date = '2024-06-01'  # Начальная дата для получения всех данных

    url = f'https://graph.facebook.com/v20.0/act_{ad_account_id}/campaigns'
    params = {'access_token': access_token}

    response = requests.get(url, params=params)
    data = response.json()

    if 'error' in data:
        print(f"Ошибка в ответе API: {data['error']}")
        return

    if 'data' not in data:
        print("Ответ API не содержит ключ 'data'")
        print("Полный ответ:", data)
        return

    print(f"Получено {len(data['data'])} кампаний")

    result = []
    for campaign in data['data']:
        next_page_url = f'https://graph.facebook.com/v20.0/{campaign["id"]}/insights'
        while next_page_url:
            insight_params = {
                'fields': 'campaign_name,campaign_id,adset_name,clicks,reach,impressions,actions,date_start,spend',
                'access_token': access_token,
                'time_range': json.dumps({'since': start_date, 'until': end_date_str}),
                'time_increment': '1'
            }
            response = requests.get(next_page_url, params=insight_params)
            insight_data = response.json()

            if 'error' in insight_data:
                print(f"Ошибка в ответе API при запросе insights: {insight_data['error']}")
                break

            if 'data' not in insight_data:
                print("Ответ API на запрос insights не содержит ключ 'data'")
                print("Полный ответ:", insight_data)
                break

            # Обрабатываем данные текущей страницы
            for record in insight_data['data']:
                lead_action = next((action for action in record.get('actions', []) if action['action_type'] == 'lead'), None)
                lead_value = int(lead_action['value']) if lead_action else 0
                spend = float(record['spend'])
                impressions = int(record['impressions'])
                clicks = int(record['clicks'])
                campaign_name = record['campaign_name']
                adset_name = record.get('adset_name', 'Unknown')

                # Определение языковой группы
                if 'русский' in campaign_name.lower():
                    campaign = 'RU'
                elif 'английский' in campaign_name.lower():
                    campaign = 'EN'
                elif 'словенский' in campaign_name.lower():
                    campaign = 'SLO'
                else:
                    campaign = campaign_name

                result.append({
                    'Дата': record['date_start'],
                    'Клики': clicks,
                    'Охват': record['reach'],
                    'Показы': impressions,
                    'Бюджет': f"{spend}".replace('.', ','),
                    'Заявки': lead_value,
                    'Кампания': campaign,
                    'Группа объявлений': adset_name
                })

            # Проверяем и переходим на следующую страницу
            next_page_url = insight_data.get('paging', {}).get('next')
            if not next_page_url:
                print("Нет следующей страницы. Переход завершён.")

    if result:
        print(f"Запись {len(result)} записей в файл")
        keys = result[0].keys()
        file_path = 'facebook_ads_data_leads_1_year.csv'
        with open(file_path, 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(result)
        
        # Добавляем метку времени в конец файла
        with open(file_path, 'a') as f:
            f.write(f"\n# Last updated: {datetime.now().isoformat()}\n")
        
        print("Данные успешно экспортированы в", file_path)
    else:
        print("Нет данных для экспорта")

if __name__ == "__main__":
    fetch_data()
