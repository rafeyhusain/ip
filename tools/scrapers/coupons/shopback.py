# coding=utf-8
# scrapy runspider shopback.py -o shopback.csv

import json, re, requests, sys, scrapy

reload(sys)
sys.setdefaultencoding("utf-8")


class StackOverflowSpider(scrapy.Spider):
    name = 'shopback'
    start_urls = ['https://www.shopback.ph/api/allStores', 'https://www.shopback.my/api/allStores',
                  'https://www.shopback.sg/api/allStores', 'https://www.shopback.co.id/api/allStores']

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    }

    def parse(self, response):
        jsonresponse = json.loads(response.body_as_unicode())
        for char, items in jsonresponse["sortedStores"].iteritems():
            for item in items:
                url = response.urljoin(item['shortname'])
                yield scrapy.Request(url, callback=self.parse_store)

    def parse_store(self, response):
        name = response.url.split("/")[3]

        i = 0
        for offer in response.css('.merchant-deal'):
            i = i + 1

            text = offer.css("h3::text").extract()[0].strip()

            try:
                code = offer.css(".the-code::attr(value)").extract()[0]
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
