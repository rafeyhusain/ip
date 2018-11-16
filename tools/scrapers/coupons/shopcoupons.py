# coding=utf-8
# scrapy runspider shopcoupons.py -o shopcoupons.csv

import re, requests, sys, scrapy

reload(sys)
sys.setdefaultencoding("utf-8")


class StackOverflowSpider(scrapy.Spider):
    name = 'shopcoupons'
    start_urls = ['https://shopcoupons.my/stores', 'https://shopcoupons.sg/stores', 'https://shopcoupons.ph/stores',
                  'https://shopcoupons.co.id/stores']

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    }

    def parse(self, response):
        for href in response.css('#stores_list a::attr(href)'):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_store)

    def parse_store(self, response):
        name = response.css('h1::text').extract()[0]

        i = 0
        for offer in response.css('.coupon-box'):
            i = i + 1

            text = offer.css("h4::text").extract()[0].strip()

            try:
                code = offer.css(".coupon-text::text").extract()[0]
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
