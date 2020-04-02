from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
import avitoparse.settings as settings
from avitoparse.spiders.avito import AvitoSpider

if __name__ == '__main__':
    craw_settings = Settings()
    craw_settings.setmodule(settings)
    crawler_proc = CrawlerProcess(settings=craw_settings)
    crawler_proc.crawl(AvitoSpider)
    crawler_proc.start()