# -*- coding: utf-8 -*-
import scrapy


class ZillowSpider(scrapy.Spider):
    name = 'zillow'
    allowed_domains = ['www.zillow.com']
    start_urls = ['https://www.zillow.com/san-francisco-ca']

    def parse(self, response):
        for pag_url in response.xpath('//nav[@aria-label="Pagination"]/ul/li/a/@href'):
            yield response.follow(pag_url, callback=self.parse)
        print(1)
