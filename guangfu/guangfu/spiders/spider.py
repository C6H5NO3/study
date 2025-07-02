import scrapy
from guangfu.items import GuangfuItem

def get_proxy():
    proxy = 'geo.iproyal.com:12321'
    proxy_auth = 'pJxVSpMD9DUYW1sj:sFILq2zO5uSTt5oG'
    return f'http://{proxy_auth}@{proxy}'

class SpiderSpider(scrapy.Spider):
    name = "spider"
    allowed_domains = ["guangfu.bjx.com.cn"]
    start_urls = ["https://guangfu.bjx.com.cn/zc/"]

    def start_requests(self):
        for url in self.start_urls:
            proxy = get_proxy()
            yield scrapy.Request(url, meta={'proxy': proxy})

    def parse(self, response):
        for each in response.xpath('//div[@class="cc-list-content"]/ul/li'):
            item = GuangfuItem()
            item['date_time'] = each.xpath('./span/text()').get(default="N/A")
            item['title'] = each.xpath('./a/text()').get(default="N/A")
            content_url = each.xpath('./a/@href').get(default="N/A")

            if content_url:
                yield response.follow(content_url, callback=self.parse_content, meta={'item': item})
            else:
                yield item

        next_page = response.xpath('//div[@class="cc-paging"]/a[last()]/@href').get()
        if next_page != 'javascript:;': 
            proxy = get_proxy()
            yield response.follow(next_page, callback=self.parse, meta={'proxy': proxy})

    def parse_content(self, response):
        item = response.meta['item']
        content = response.xpath('//div[@class="cc-article"]/p//text()').getall()
        item['content'] = ''.join(content).strip()
        yield item