from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
import blogparse.settings as settings
from blogparse.spiders.habr_weekly import HabrWeeklySpider
from blogparse.spiders.gb_blog import GbBlogSpider


if __name__ == '__main__':
    craw_settings = Settings()
    craw_settings.setmodule(settings)
    crawler_proc = CrawlerProcess(settings=craw_settings)
    crawler_proc.crawl(HabrWeeklySpider)
    crawler_proc.start()


# Необходимо обойти все странички популярного за неделю, ( delay рекомендую ставить около 600mc не меньше а лучше 1 секунду)
#
# Извлекаем следующие данные:
# - заголовок
# - имя автора
# - ссылка на страницу автора
# - дата публикации
# - список тегов
# - список хабов
# - количество комментариев
# - дата парсинга (когда совершен парсинг)
