# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from pymongo import MongoClient
import datetime


class BlogparsePipeline(object):
    def __init__(self):
        client = MongoClient('mongodb://localhost:27017/')
        self.db = client['habr_weekly_with_scrapy']


    def process_item(self, item, spider):
        collection = self.db[spider.name]
        time = datetime.datetime.now()
        item['date_parse'] = time
        collection.insert_one(item)
        return item
