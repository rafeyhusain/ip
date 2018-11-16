# coding=utf-8
# scrapy runspider saleduck.py -o saleduck.csv

import re, requests, sys, scrapy

reload(sys)
sys.setdefaultencoding("utf-8")


class StackOverflowSpider(scrapy.Spider):
    name = 'saleduck'
    start_urls = ['http://www.saleduck.com.ph/online-shops', 'http://www.saleduck.com.my/online-shops',
                  'http://www.saleduck.co.id/online-shops', 'http://www.saleduck.com.sg/online-shops',
                  'http://www.saleduck.co.th/online-shops']

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    }

    def parse(self, response):
        for href in response.css('.webshops .content a::attr(href)'):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_store)

    def parse_store(self, response):
        name = response.css('.webshop-logo .box-icon img::attr(alt)').extract()[0]

        i = 0
        for offer in response.css(".valid-deals-container .deal-item"):
            i = i + 1

            text = offer.css("h4.deal-title span::attr(title)").extract()[0].strip()

            otype = offer.css(".row .btn::text").extract()[0]

            if otype == "Show Promo Code!":
                otype = "code"
            else:
                otype = "promo"

            url = response.url

            yield {
                'store': name,
                'url': url,
                'type': otype,
                'text': text,
                'code': "n/a",
            }
