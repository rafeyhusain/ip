# coding=utf-8
# scrapy runspider cuponation.py -o cuponation.csv

import re, requests, sys, scrapy

reload(sys)
sys.setdefaultencoding("utf-8")


class StackOverflowSpider(scrapy.Spider):
    name = 'cuponation'
    start_urls = ['https://www.cuponation.com.sg/allshop', 'https://www.cuponation.com.my/allshop']

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    }

    def parse(self, response):
        for href in response.css('.cn-alphabet-list .group a::attr(href)'):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_store)

    def parse_store(self, response):
        name = response.css('.cn-retailer-logo::attr(data-retailer_name)').extract()[0]

        i = 0
        for offer in response.css('.voucher-list .cn-voucher'):
            i = i + 1

            try:
                code = offer.css(".code-field").extract()[0]
                otype = "coupon"
            except:
                code = "n/a"
                otype = "deal"
            text = offer.css("h3 span::text").extract()[0].strip()

            url = response.url

            yield {
                'store': name,
                'url': url,
                'type': otype,
                'text': text,
                'code': code,
                'url': url,
            }
