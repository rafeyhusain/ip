# coding=utf-8
# scrapy runspider priceza.py -o priceza.csv

import re, requests, sys, scrapy, urlparse

reload(sys)
sys.setdefaultencoding("utf-8")


class StackOverflowSpider(scrapy.Spider):
    name = 'priceza'
    start_urls = ['http://www.priceza.com/merchant/', 'http://www.priceza.co.id/merchant/',
                  'http://www.priceza.com.sg/merchant/', 'http://www.priceza.com.my/merchant/',
                  'http://www.priceza.com.ph/merchant/', 'http://www.priceza.com.vn/merchant/']

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    }

    def parse(self, response):  # start from the merchant list and open every link
        for item in response.css('.merchantBox'):
            url = response.urljoin(item.css('a::attr(href)').extract()[0])
            request = scrapy.Request(url, callback=self.parse_merchant)
            yield request

    def parse_merchant(self, response):  # look for the product number on the page
        url = response.urljoin(response.css('#detail-tabs a::attr(href)').extract()[1])
        request = scrapy.Request(url, callback=self.parse_products)
        yield request

    def parse_products(self, response):  # collect information
        merchant = response.css('h1 span::text').extract()[0]
        try:
            products = int(re.sub("[^0-9]", "", response.css('.head.group .head-name h2 small::text ').extract()[0]))
        except Exception, e:
            products = 0
        yield {
            'domain': urlparse.urlparse(response.url).netloc,
            'path': urlparse.urlparse(response.url).path,
            'merchant': merchant,
            'products': products,
        }
