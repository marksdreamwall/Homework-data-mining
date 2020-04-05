# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline
import datetime


class AvitoparsePipeline(object):
    def __init__(self):
        client = MongoClient('mongodb://localhost:27017/')
        self.db = client['instagram']

    def process_item(self, item, spider):
        collection = self.db['followers']
        collection_2 = self.db['followings']
        collection_3 = self.db['posts']
        if 'followers' in item: # наверное можно сделать как то более аккуратно...
            collection.insert_one(item)
        if 'followings' in item:
            collection_2.insert_one(item)
        if 'posts' in item:
            collection_3.insert_one(item)
        return item


class ImgPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item.get('photos'):
            for img_url in item['photos']:
                try:
                    yield scrapy.Request(img_url)
                except Exception as e:
                    pass
    def item_completed(self, results, item, info):
        if results:
            item['photos'] = [itm[1] for itm in results]
        return item
