# -*- coding: utf-8 -*-
from copy import deepcopy
import scrapy
import re
import json
from urllib.parse import urljoin, urlencode


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    graphql_url = 'https://www.instagram.com/graphql/query/?'
    start_urls = ['https://instagram.com/']
    parse_users = ['nba']
    variables = {"id": "",
                 "include_reel": True,
                 "fetch_mutual": False,
                 "first": 100,
                 }

    def __init__(self, logpass:tuple, **kwargs):
        self.login, self.pwd = logpass
        self.query_hash_followers = 'c76146de99bb02f6415203be841dd25a'
        self.query_hash_followings = 'd04b0a864b4b54837c0d870b0e77e076'
        self.query_hash_posts = 'd496eb541e5c789274548bf473cc553e'
        super().__init__(**kwargs)

    def parse(self, response):
        login_url = 'https://www.instagram.com/accounts/login/ajax/'
        csrf_token = self.fetch_csrf_tokne(response.text)

        yield scrapy.FormRequest(
            login_url,
            method='POST',
            callback=self.main_parse,
            formdata={'username': self.login, 'password': self.pwd},
            headers={'X-CSRFToken': csrf_token}
        )

    def main_parse(self, response):
        j_resp = json.loads(response.text)
        if j_resp.get("authenticated"):
            for u_name in self.parse_users:
                yield response.follow(
                    urljoin(self.start_urls[0], u_name),
                    callback=self.parse_user,
                    cb_kwargs={'user_name': u_name}
                )

    def parse_user(self, response, user_name: str):
        user_id = self.fetch_user_id(response.text, user_name)
        user_vars = deepcopy(self.variables)
        user_vars.update({'id': user_id})
        url = self.make_graphql_url(user_vars)
        url_f = self.make_graphql_url_followings(user_vars)
        url_p = self.make_graphql_url_posts(user_vars)
        yield response.follow(
            url,
            callback=self.parse_followers,
            cb_kwargs={'user_vars': user_vars,
                       'user_name': user_name}
        )
        yield response.follow(
            url_f,
            callback=self.parse_followings,
            cb_kwargs={'user_vars': user_vars,
                       'user_name': user_name}
        )
        yield response.follow(
            url_p,
            callback=self.parse_posts,
            cb_kwargs={'user_vars': user_vars,
                       'user_name': user_name}
        )

    """ Сбор данных о подписчиках"""
    def parse_followers(self, response, user_vars, user_name):
        j_response = json.loads(response.text)
        if j_response['data']['user']['edge_followed_by']['page_info']['has_next_page']:
            user_vars.update({'after': j_response['data']['user']['edge_followed_by']['page_info']['end_cursor']})
            url = self.make_graphql_url(user_vars)
            yield response.follow(
                url,
                callback=self.parse_followers,
                cb_kwargs={'user_vars': user_vars,
                           'user_name': user_name}
            )

        followers = j_response['data']['user']['edge_followed_by']['edges']
        for follower in followers:
            yield {'user_name': user_name, 'user_id': user_vars['id'], 'followers': follower['node']}

    """ Сбор данных о подписках"""
    def parse_followings(self, response, user_vars, user_name):
        j_response = json.loads(response.text)
        if j_response['data']['user']['edge_follow']['page_info']['has_next_page']:
            user_vars.update({'after': j_response['data']['user']['edge_follow']['page_info']['end_cursor']})
            url_f = self.make_graphql_url_followings(user_vars)
            yield response.follow(
                url_f,
                callback=self.parse_followings,
                cb_kwargs={'user_vars': user_vars,
                           'user_name': user_name}
            )

        followings = j_response['data']['user']['edge_follow']['edges']
        for following in followings:
            yield {'user_name': user_name, 'user_id': user_vars['id'], 'followings': following['node']}

    """ Сбор данных о постах"""
    def parse_posts(self, response, user_vars, user_name):
        j_response = json.loads(response.text)
        if j_response['data']['user']['edge_owner_to_timeline_media']['page_info']['has_next_page']:
            user_vars.update({'after': j_response['data']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']})
            url_p = self.make_graphql_url_posts(user_vars)
            yield response.follow(
                url_p,
                callback=self.parse_posts,
                cb_kwargs={'user_vars': user_vars,
                           'user_name': user_name}
            )

        posts = j_response['data']['user']['edge_owner_to_timeline_media']['edges']
        for post in posts:
            yield {'user_name': user_name, 'user_id': user_vars['id'], 'posts': post['node']}


    def fetch_csrf_tokne(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')

    def make_graphql_url(self, user_vars):
        return f'{self.graphql_url}query_hash={self.query_hash_followers}&{urlencode(user_vars)}'

    def make_graphql_url_followings(self, user_vars):
        return f'{self.graphql_url}query_hash={self.query_hash_followings}&{urlencode(user_vars)}'

    def make_graphql_url_posts(self, user_vars):
        return f'{self.graphql_url}query_hash={self.query_hash_posts}&{urlencode(user_vars)}'
