# coding=utf-8
# scrapy runspider flipit.py -o flipit.csv

import re, requests, sys, scrapy

reload(sys)
sys.setdefaultencoding("utf-8")


class StackOverflowSpider(scrapy.Spider):
    name = 'flipit'
    start_urls = ['http://www.flipit.com/sg/all-shops', 'http://www.flipit.com/my/all-shops',
                  'http://www.flipit.com/id/all-shops']

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    }

    def parse(self, response):
        for href in response.css('.shop-name a::attr(href)'):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_store)

        for href in response.css('.alphabet a::attr(href)'):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse)

    def parse_store(self, response):
        name = response.css('h1::text').extract()[0]

        i = 0
        for offer in response.css('#content .shoppage')[0].css('.block:not(.expired-deal) .offer-holder'):
            i = i + 1

            try:
                offer.css(".kccode::text").extract()[0]
                otype = "code"
            except Exception, e:
                otype = "promo"

            text = offer.css("h3 span::text").extract()[0].strip()

            url = response.url

            yield {
                'store': name,
                'url': url,
                'type': otype,
                'text': text,
                'code': "n/a",
                'url': url,
            }
