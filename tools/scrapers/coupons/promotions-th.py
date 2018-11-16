# coding=utf-8
# scrapy runspider promotions-th.py -o promotions-th.csv

import re, requests, sys, scrapy

reload(sys)
sys.setdefaultencoding("utf-8")


class StackOverflowSpider(scrapy.Spider):
    name = 'promotions-th'
    start_urls = ['http://promotions.co.th/coupon/stores']

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    }

    def parse(self, response):
        for href in response.css('.stores a::attr(href)'):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_store)

    def parse_store(self, response):
        name = response.css('h1::text').extract()[0]

        i = 0
        for offer in response.css('.coupon.status-publish'):
            i = i + 1

            text = offer.css("h3 a::text").extract()[0].strip()

            code = offer.css(".link-holder a::attr(data-clipboard-text)").extract()[0]

            if code == "Click to Redeem":
                otype = "deal"
                code = ""
            else:
                otype = "code"

            url = response.url

            yield {
                'store': name,
                'url': url,
                'type': otype,
                'text': text,
                'code': code,
                'url': url,
            }
