import bs4
import requests
from bs4 import BeautifulSoup
import re
from pymongo import MongoClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import Session
from sql_models import Post, Writer, Comment_author


headers = {'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:74.0) Gecko/20100101 Firefox/74.0'}
base_url = 'https://habr.com'
start_url = 'https://habr.com/ru/top/weekly/'


response = requests.get(start_url, headers=headers)
soup = BeautifulSoup(response.text, 'lxml')


def next_page(soup:bs4.BeautifulSoup) -> str:
    np = soup.select_one('#next_page')['href']
    return f'{base_url}{np}' if np else None


def get_page(url):
    while url:
        print(url)
        response = requests.get(url, headers=headers)
        soup = bs4.BeautifulSoup(response.text, 'lxml')
        yield soup
        url = next_page(soup)


def get_post_url(soup:bs4.BeautifulSoup) -> set:
    a = soup.find_all('a', class_='post__title_link')
    return set(itm["href"] for itm in a)


def comment_author_info(post_url:str) -> dict: # функция для записи всех коментаторов и их адресов
    ca_data = {'ca_name': [],
               'ca_url': []}
    response = requests.get(post_url, headers=headers)
    soup = bs4.BeautifulSoup(response.text, 'lxml')
    all_ca_urls = soup.select('div:nth-child(3) > a:nth-child(1)')
    for itm in all_ca_urls:
        ca_data['ca_url'].append(itm['href'])
    all_ca_names = soup.select('div:nth-child(3) > a:nth-child(1) > span:nth-child(2)')
    for itm in all_ca_names:
            ca_data['ca_name'].append(itm.text)
    return ca_data


def get_post_data(post_url: str) -> dict:
    tmp_data = {'url': '',
                     'title': '',
                     'date_time':'',
                     'comments_count': '',
                     'comment_author': {},
                     'writer': {'name': '', 'writer_url': ''}}
    response = requests.get(post_url, headers=headers)
    soup = bs4.BeautifulSoup(response.text, 'lxml')
    tmp_data['url'] = post_url
    tmp_data['title'] = soup.find('span', class_='post__title-text').text
    tmp_data['date_time'] = soup.find('span', class_='post__time').text # не смог вытащить именно DATETIME
    tmp_data['comments_count'] = re.findall('\d+',
                                            (soup.find('span', {'id': 'comments_count'}).text))
    tmp_data['comment_author'] = comment_author_info(post_url)
    tmp_data['writer']['name'] = soup.select_one('.post__user-info > span:nth-child(2)').text
    tmp_data['writer']['writer_url'] = soup.select_one('.post__user-info')['href']
    return tmp_data

def clear_file_name(url: str):
    return url.replace('/', '_')


Base = declarative_base()


if __name__ == '__main__':
    # client = MongoClient('mongodb://localhost:27017/')
    # db = client['habr_top_weekly']
    engine = create_engine('sqlite:///habr_weekly.db')
    Base.metadata.create_all(engine)
    session_db = sessionmaker(bind=engine)
    session = session_db()

    for soup in get_page(start_url):
        posts = get_post_url(soup)
        data = [get_post_data(url) for url in posts]
        # db['top_weekly_posts'].insert_many(data)
        dl = len(data)
        i = 0
        while i != dl:
            post = Post(data[i]['title'],
                        data[i]['url'],
                        data[i]['date_time'])
            writer = Writer(data[i]['writer']['name'],
                            data[i]['writer']['writer_url'])
            n = 0
            m = 0
            while n != len(data[i]['comment_author']['ca_name']):
                ca = Comment_author(data[i]['comment_author']['ca_name'][n],
                                    data[i]['comment_author']['ca_url'][m])
                n+=1
                m+=1
                session.add(ca)
                try:
                    session.commit()
                except Exception as e:
                    session.rollback()
                finally:
                    session.close()
            session.add(post)
            session.add(writer)

            try:
                session.commit()
            except Exception as e:
                session.rollback()
            finally:
                session.close()
            i+= 1
            print(1)

# 1. Заполнение таблиц происходит нормально как для Монго так и для SQL
# 2. Не получилось наладить связи между таблицами. не могу понять где ошибка (код закоменчен)
# 3. Не придумал более простого способа заполнения SQL таблиц.
# 4. Поле post&date_time - str. Не получилось спарсить именно значение даты/времени