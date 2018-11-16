# coding=utf-8
# scrapy runspider priceprice.py -o priceprice.csv

import re, requests, sys, scrapy

reload(sys)
sys.setdefaultencoding("utf-8")


class StackOverflowSpider(scrapy.Spider):
    name = 'shopback'
    start_urls = ['http://ph.priceprice.com/coupons/stores/', 'http://id.priceprice.com/coupons/stores/',
                  'http://th.priceprice.com/coupons/stores/']

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    }

    def parse(self, response):
        for href in response.css('.nameList a::attr(href)'):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_store)

    def parse_store(self, response):
        name = response.css('.info .name::text').extract()[0]

        i = 0
        for offer in response.css('.list02 .code'):
            i = i + 1

            text = offer.css(".sttl::text").extract()[0].strip()

            try:
                code = offer.css(".couponCodeBtn01 span em::text").extract()[0]
                code = 'n/a'
                otype = "code"
            except Exception, e:
                code = ""
                otype = "deal"

            url = response.url

            yield {
                'store': name,
                'url': url,
                'type': otype,
                'text': text,
                'code': code,
                'url': url,
            }
