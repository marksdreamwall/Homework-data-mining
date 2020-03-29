# -*- coding: utf-8 -*-
import scrapy


class HabrWeeklySpider(scrapy.Spider):
    name = 'habr_weekly'
    allowed_domains = ['habr.com']
    start_urls = ['https://habr.com/ru/top/weekly']

    def parse(self, response):
        next_url = response.xpath('//a[contains(@class, "toggle-menu__item-link_pagination")]/@href').extract()
        for itm in next_url:
            yield response.follow(itm, callback=self.parse)

        for post_url in response.xpath('//a[contains(@class, "post__title_link")]/@href').extract():
            yield response.follow(post_url, callback=self.post_parse)

    def clear_tags(self, tags_hubs):  # не знаю где лучше создать эту функцию.
        trash = []  # тэги собираются криво вместе с хабами
        for itm in tags_hubs:
            if itm.startswith('\n'):
                trash.append(itm)
        return list(set(tags_hubs) - set(trash)) # возвращает чистый список тэгов

    def post_parse(self, response):
        th = response.xpath('//a[contains(@class, "inline-list__item-link post__tag")]/text()').extract()
        data = {
            'title': response.xpath('//span[contains(@class, "post__title-text")]/text()').extract_first(),
            'author_name': response.xpath('//span[contains(@class, "user-info__nickname_small")]/text()').extract_first(),
            'author_url': response.xpath('//a[contains(@class, "post__user-info")]/@href').extract_first(),
            'post_date': response.xpath('//span[contains(@class, "post__time")]').re(r'\d+\-\d+\-\d+\w\d+\:\d+'),
            'tags': self.clear_tags(th),
            'hubs': response.xpath('//a[contains(@class, "inline-list__item-link hub-link")]/text()').extract(),
            'comments_count': response.xpath('//span[contains(@class, "comments-section__head-counter")]/text()').re(r'\d+')
        }
        yield data



