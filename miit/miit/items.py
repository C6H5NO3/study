# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MiitItem(scrapy.Item):
    title = scrapy.Field()
    date_time  = scrapy.Field()
    content = scrapy.Field()