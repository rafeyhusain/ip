# coding=utf-8
# scrapy runspider diskonaja.py -o diskonaja.csv

import re, requests, sys, scrapy

reload(sys)
sys.setdefaultencoding("utf-8")


class StackOverflowSpider(scrapy.Spider):
    name = 'diskonaja'

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    }

    def start_requests(self):
        r = []
        for i in [0, 60, 120, 180]:
            r.append(scrapy.FormRequest("https://www.diskonaja.com/wp-admin/admin-ajax.php",
                                        formdata={'action': 'load_more', 'num': "%s" % i, 'type': 'merchant'},
                                        callback=self.parse))
        return r

    def parse(self, response):
        for href in response.css('.item::attr(onclick)'):
            url = response.urljoin(href.extract().split("'")[1])
            yield scrapy.Request(url, callback=self.parse_store)

    def parse_store(self, response):
        name = response.css('.merchant_logo img::attr(alt)').extract()[0].replace("Logo ", "")

        i = 0
        for offer in response.css('.promo-content .promo-item'):
            i = i + 1

            text = offer.css(".promo-title h3::text").extract()[0].strip()

            code = offer.css(".promo_type .row div::text").extract()[0].strip()

            if code == "Get Deal":
                otype = "deal"
            else:
                otype = "code"

            url = response.url

            yield {
                'store': name,
                'url': url,
                'type': otype,
                'text': text,
                'code': "n/a",
            }
