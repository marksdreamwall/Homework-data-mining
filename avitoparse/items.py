# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst


class AvitoparseItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def clean_photo(values):
    if values[:2] == '//':
        return f'http:{values}'
    return values


def clean_date(value):
    return value.replace('\n   ', '').replace("  ", '')


def clean_author_name(value):
    return value.replace('\n', '')


def create_author_url(value):
    return f'https://www.avito.ru{value}'


class AvitoRealEstateItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field(output_processor=TakeFirst())
    title = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field(input_processor=MapCompose(clean_photo))
    date = scrapy.Field(scrapy.Field(input_processor=MapCompose(clean_date),
                                     output_processor=TakeFirst()))
    author_name = scrapy.Field(input_processor=MapCompose(clean_author_name),
                               output_processor=TakeFirst())
    author_url = scrapy.Field(input_processor=MapCompose(create_author_url),
                              output_processor=TakeFirst())
    floor = scrapy.Field(output_processor=TakeFirst())
    house_floors = scrapy.Field(output_processor=TakeFirst())
    house_type = scrapy.Field(output_processor=TakeFirst())
    room_count = scrapy.Field(output_processor=TakeFirst())
    total_area = scrapy.Field(output_processor=TakeFirst())
    kitchen_area = scrapy.Field(output_processor=TakeFirst())


class ZillowItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field(output_processor=TakeFirst())
    adress = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(output_processor=TakeFirst())
    sqft = scrapy.Field()
    photos = scrapy.Field()
