# coding=utf-8
# scrapy runspider ivouchercodes.py -o ivouchercodes.csv

import re, requests, sys, scrapy

reload(sys)
sys.setdefaultencoding("utf-8")


class StackOverflowSpider(scrapy.Spider):
    name = 'ivouchercodes'
    start_urls = ['http://ivouchercodes.ph/stores', 'http://ivouchercodes.sg/stores',
                  'http://yavouchercodes.com/stores']

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    }

    def parse(self, response):
        for href in response.css('.browse_stores a::attr(href)'):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_store)

    def parse_store(self, response):
        name = response.css('meta[property="og:title"]::attr(content)').extract()[0].strip()

        i = 0
        for offer in response.css('#All .loop_div'):
            i = i + 1

            otype = offer.css(".store-image .v-title::text").extract()[0].strip()
            text = offer.css("h3 a::text").extract()[0].strip()

            try:
                code = offer.css(".coupon-code-link1::attr(data-clipboard-text)").extract()[0]
            except Exception, e:
                code = ""

            url = response.url

            yield {
                'store': name,
                'url': url,
                'type': otype,
                'text': text,
                'code': code,
                'url': url,
            }
