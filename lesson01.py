# JSON файлы по категориям, содержащие продукты этой категории
# Имя - название категории.
# Словарь из продуктов
# Выборка только из акционных продуктов

import requests
import json
import time

start_url = 'https://5ka.ru/api/v2/special_offers/'
cat_url = 'https://5ka.ru/api/v2/categories/'
headers = {'User-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'}


resp = requests.get(cat_url, headers=headers)
cat_data = resp.json()
cat_tag = []    # список значений для перехода по категориям
cat_names = []  # список имен категорий
z = 0
while z != 45:  # не понял, как узнать кол-во пар ключ-значение, поэтому 45 задано в ручную
    cat_tag.append(cat_data[z].get('parent_group_code'))
    cat_names.append(cat_data[z].get('parent_group_name'))
    z+=1


def x5ka(url, params):
    result = []
    while url:
        response = requests.get(url, headers=headers, params=params) if params else requests.get(url, headers=headers)
        params = None
        data = response.json()
        result.extend(data.get('results'))
        url = data.get('next')
        time.sleep(1)
    return result


cat_count = len(cat_tag)    # длина списка


if __name__ == '__main__':
    i = 0
    while i < cat_count:
        data = x5ka(start_url, {'categories': cat_tag[i]})  # параметр - код категории
        with open('{}.json'.format(cat_names[i]), 'w') as file:
           file.write(json.dumps(data))
        i+=1

