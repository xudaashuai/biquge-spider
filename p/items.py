# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class BookItem(scrapy.Item):
    id = scrapy.Field()
    _id = scrapy.Field()
    ca_id = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    desc = scrapy.Field()
    last_updated = scrapy.Field()
    chapters = scrapy.Field()
    image = scrapy.Field()
    collection = 'book'

class ChapterItem(scrapy.Item):
    _id = scrapy.Field()
    id = scrapy.Field()
    book_full_id = scrapy.Field()
    title = scrapy.Field()
    link = scrapy.Field()
    content = scrapy.Field()
    collection = 'chapter'
