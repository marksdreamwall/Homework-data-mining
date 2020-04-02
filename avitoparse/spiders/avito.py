# -*- coding: utf-8 -*-
import scrapy
from scrapy.loader import ItemLoader
from avitoparse.items import AvitoRealEstateItem


class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['avito.ru']
    start_urls = ['https://www.avito.ru/moskva/kvartiry']

    def parse(self, response):
        for num in response.xpath('//div[@data-marker="pagination-button"]//span/text()'):
            try:
                tmp = int(num.get())
                yield response.follow(f'/moskva/kvartiry?p={tmp}', callback=self.parse)

            except TypeError as e:
                continue
            except ValueError as e:
                continue

        for ads_url in response.xpath('//div[contains(@class, "snippet-title-row")]//a[contains(@class, "snippet-link")]/@href'):
            yield response.follow(ads_url, callback=self.ads_parse)

    def ads_parse(self, response):
        item = ItemLoader(AvitoRealEstateItem(), response)
        item.add_value('url', response.url)
        item.add_xpath('title', '//span[contains(@class, "title-info-title-text")]/text()')
        item.add_xpath('photos', '//div[contains(@class, "gallery-img-frame")]/@data-url')
        item.add_xpath('date', '//div[contains(@class, "title-info-metadata-item-redesign")]/text()')
        item.add_xpath('author_url', '//div[contains(@class, "seller-info-name js-seller-info-name")]//a/@href')
        item.add_xpath('author_name', '//div[contains(@class, "seller-info-name js-seller-info-name")]//a/text()')
        try:
            item.add_value('floor', response.xpath('//li//span[contains(text(), "Этаж:")]/parent::node()/text()').re(r'\d+'))
            item.add_value('house_floors', response.xpath('//li//span[contains(text(), "Этажей в доме:")]/parent::node()/text()').re(r'\d+'))
            item.add_value('house_type', response.xpath('//li//span[contains(text(), "Тип дома:")]/parent::node()/text()')[1].extract())
            item.add_value('room_count', response.xpath('//li//span[contains(text(), "Количество комнат:")]/parent::node()/text()')[1].extract())
            item.add_value('total_area', response.xpath('//li//span[contains(text(), "Общая площадь:")]/parent::node()/text()')[1].extract())
            item.add_value('kitchen_area', response.xpath('//li//span[contains(text(), "Площадь кухни:")]/parent::node()/text()')[1].extract())
        except IndexError as e:
            print(f'{response.url} - Данные не полные!') # обработка ошибки, возникающей если отсутствуют данные на странице.
        finally:
            yield item.load_item()

# - телефон не получилось.