import scrapy
import pymongo
import re
from scrapy.loader import ItemLoader
from datetime import datetime

client = pymongo.MongoClient(host='localhost', port=27017)


class Book(scrapy.Item):
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


class Chapter(scrapy.Item):
    _id = scrapy.Field()
    id = scrapy.Field()
    book_full_id = scrapy.Field()
    title = scrapy.Field()
    link = scrapy.Field()
    content = scrapy.Field()
    collection = 'chapter'


class MainspiderSpider(scrapy.Spider):
    name = 'bqg'
    allowed_domains = ['www.biquge.com']
    start_urls = ['https://www.biquge.com/searchbook.php?keyword=%E4%BA%BA']
    all_words = set()

    def parse(self, response):
        for item in response.xpath('//a/@href').extract():
            if re.match(r"^/[\d_]+/$", item):
                yield scrapy.Request('https://www.biquge.com' + item, callback=self.parse_detail, dont_filter=False)
        next = response.css('.next::attr(href)').extract()
        if next.__len__() > 0:
            yield scrapy.Request('https://www.biquge.com' + next[0], callback=self.parse, dont_filter=False)

    def parse_detail(self, response):
        all_book_id = response.url.split('/')[3]
        [ca_id, book_id] = all_book_id.split('_')

        title = response.css('#info > h1::text').extract()[0]
        for item in title:
            yield scrapy.Request('https://www.biquge.com/searchbook.php?keyword=' + item, callback=self.parse, dont_filter=False)
        items = list(map(lambda x: {
            'link': 'https://www.biquge.com' + x.attrib['href'],
            'book_full_id': x.attrib['href'].split('/')[1],
            'id': x.attrib['href'].split('/')[2].split('.')[0],
            "title": x.xpath('text()').extract()[0]
        }, response.xpath('//*[@id="list"]/dl/dt[2]/following::dd/a')))
        yield Book({
            '_id': book_id,
            'ca_id': ca_id,
            'id': book_id,
            'title': title,
            'desc': response.css('#intro::text').extract()[0],
            'image': 'https:' + response.css('#fmimg > img::attr(src)').extract()[0],
            'author': response.css('#info > p:nth-child(2)::text').extract()[0].split('：')[1],
            'last_updated': int(datetime.strptime(response.css('#info > p:nth-child(4)::text').extract()[0].split('：')[1], '%Y-%m-%d %H:%M:%S').timestamp()),
            'chapters': items
        })
        for chapter in items:
            yield scrapy.Request(chapter['link'], callback=self.parse_chapter, dont_filter=False, meta=chapter)

    def parse_chapter(self, response):
        content = response.css('#content::text').extract()
        yield Chapter({
            '_id': response.meta['id'],
            'link': response.meta['link'],
            'book_full_id': response.meta['book_full_id'],
            'id': response.meta['id'],
            "title": response.meta['title'],
            "content": content
        })
