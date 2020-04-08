import os
from pathlib import Path
from dotenv import load_dotenv

from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
import avitoparse.settings as settings
from avitoparse.spiders.avito import AvitoSpider
from avitoparse.spiders.instagram import InstagramSpider
from avitoparse.spiders.zillow import ZillowSpider


env_path = Path(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)

if __name__ == '__main__':
    craw_settings = Settings()
    craw_settings.setmodule(settings)
    crawler_proc = CrawlerProcess(settings=craw_settings)
    crawler_proc.crawl(ZillowSpider)
    # crawler_proc.crawl(InstagramSpider, logpass=(os.getenv('INST_LOGIN'), os.getenv('INST_PWD')))
    crawler_proc.start()