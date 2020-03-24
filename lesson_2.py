import bs4
import requests
from bs4 import BeautifulSoup
import json

# todo Обойти список статей, с использованием библиотеки BS4
headers = {'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:74.0) Gecko/20100101 Firefox/74.0'}
base_url = 'https://geekbrains.ru'
start_url = 'https://geekbrains.ru/posts'

response = requests.get(start_url, headers=headers)
soup = BeautifulSoup(response.text, 'lxml')


def next_page(soup:bs4.BeautifulSoup) -> str:
    ul = soup.find('ul', class_='gb__pagination')
    a = ul.find(lambda tag: tag.name == 'a' and tag.text == '›')
    return f'{base_url}{a["href"]}' if a else None


def get_page(url):
    while url:
        print(url)
        response = requests.get(url, headers=headers)
        soup = bs4.BeautifulSoup(response.text, 'lxml')
        yield soup
        url = next_page(soup)


def get_post_url(soup:bs4.BeautifulSoup) -> set:
    post_a = soup.select('div.post-items-wrapper div.post-item a')
    return set(f'{base_url}{a["href"]}' for a in post_a)


def get_post_data(post_url:str) -> dict:
    template_data = {'url': '',
                     'title': '',
                     'post_img_url': '',
                     'tags': [],
                     'writer': {'name': '', 'writer_url': ''}}
    response = requests.get(post_url, headers=headers)
    soup = bs4.BeautifulSoup(response.text, 'lxml')
    template_data['url'] = post_url
    template_data['title'] = soup.select_one('article h1.blogpost-title').text
    template_data['post_img_url'] = soup.find('div', class_='blogpost-content').find('img')['src']
    template_data['tags'] = {itm.text:f'{base_url}{itm["href"]}' for itm in soup.select('article a.small')}
    template_data['writer']['name'] = soup.select_one('.text-lg').text
    template_data['writer']['writer_url'] = f"{base_url}{soup.find('div', class_='col-md-5').find('a')['href']}"
    return template_data


def clear_file_name(url: str):
    return url.replace('/', '_')


if __name__ == '__main__':
    all_tags = {}

    for soup in get_page(start_url):
        posts = get_post_url(soup)
        data = [get_post_data(url) for url in posts]

        for post in data:
            file_name = clear_file_name(post['url'])

            for name, url in post['tags'].items():
                if not all_tags.get(name):    # следующие 3 строки взяты из разбора дз
                    all_tags[name] = {'posts': []}
                all_tags[name]['url'] = url
                all_tags[name]['posts'].append(post['url'])

                with open(f'{file_name}.json', 'w') as file:
                    file.write(json.dumps(post))

    with open('tags.json', 'w') as file:
        file.write(json.dumps(all_tags))
        print(1)



