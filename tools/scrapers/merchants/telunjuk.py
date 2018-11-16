# coding=utf-8
# scrapy runspider telunjuk.py -o telunjuk.csv > telunjuk_print.log
# scrapy runspider telunjuk.py > telunjuk.csv 2> telunjuk_print.log

import re, requests, sys, scrapy, urlparse

reload(sys)
sys.setdefaultencoding("utf-8")


class StackOverflowSpider(scrapy.Spider):
    name = 'telunjuk'

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    }

    start_urls = ['https://www.telunjuk.com/kategori']

    def parse(self, response):  # go to categories
        for item in response.css("#main-container a::attr(href)").extract():
            url = 'https://www.telunjuk.com' + item
            request = scrapy.Request(url, callback=self.parse_products)
            yield request

    def parse_products(self, response):  # collect information from side table, only relative values
        for item in response.css('#merchant .row'):
            merchant = item.css('.col-md-10 label::text').extract()[0].split(" ")[0]
            products = re.sub("[^0-9]", "", str(item.css('.col-md-10 label::text').extract()))
            yield {
                'domain': urlparse.urlparse(response.url).netloc,
                'path': urlparse.urlparse(response.url).path,
                'merchant': merchant,
                'products': products,
            }
