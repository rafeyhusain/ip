# coding=utf-8
# scrapy runspider picodi.py -o picodi.csv

import re, requests, sys, scrapy

reload(sys)
sys.setdefaultencoding("utf-8")


class StackOverflowSpider(scrapy.Spider):
    name = 'picodi'
    start_urls = ['https://www.picodi.com/hk/retailers', 'https://www.picodi.com/id/retailers',
                  'https://www.picodi.com/my/retailers', 'https://www.picodi.com/ph/retailers',
                  'https://www.picodi.com/sg/retailers', 'https://www.picodi.com/th/retailers',
                  'https://www.picodi.com/vn/retailers']

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    }

    def parse(self, response):
        for href in response.css('.item a::attr(href)'):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_store)

    def parse_store(self, response):
        name = response.css('.breadcrumb li::text').extract()[-1]

        i = 0
        for offer in response.css('.offer'):
            i = i + 1

            otype = offer.css(".offer_label span::text").extract()[0].lower().strip()
            text = offer.css("h3 a::text").extract()[0].strip()

            try:
                code = "****" + offer.css(".in::text").extract()[0]
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
