# coding=utf-8
# scrapy runspider lazada.py -o lazada.csv

import re, requests, sys, scrapy

reload(sys)
sys.setdefaultencoding("utf-8")


class StackOverflowSpider(scrapy.Spider):
    name = 'lazada'
    start_urls = [l.strip() for l in open('/home/ubuntu/lazada/lazada-urls.csv').readlines()]

    custom_settings = {
        'CONCURRENT_REQUESTS': 128,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 128,
        'LOG_LEVEL': 'INFO',
        'COOKIES_ENABLED': False,
        'RETRY_ENABLED': False,
        'DOWNLOAD_TIMEOUT': 15,
        'REDIRECT_ENABLED': True,
        'USER_AGENT': 'scrapybot',
    }

    def parse(self, response):

        try:
            category = response.css('.breadcrumb__list li:nth-child(2) a span::text').extract()[0]
        except Exception, e:
            try:
                category = response.css('.breadcrumb__list li:nth-child(1) a span::text').extract()[0]
            except Exception, e:
                category = ""

        name = response.css('h1::text').extract()[0].strip()
        brand = response.css('.prod_header_brand_action a span::text').extract()[0]

        i = 0
        for offer in response.css('.product-multisource__source'):
            i = i + 1

            merchant = offer.css('.product__seller__name__anchor span::text').extract()[0].strip()

            price = re.sub("[^0-9]", "", offer.css('.product-multisource__source__price__amount').extract()[0]),

            yield {
                'url': response.url,
                'category': category,
                'product': name,
                'brand': brand,
                'position': i,
                'merchant': merchant,
                'price': price,
            }
