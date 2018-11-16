# coding=utf-8
# scrapy runspider pricearea.py -o pricearea.csv
# scrapy runspider pricearea.py -o pricearea.csv --logfile=pricearea.log > priceareaprint.log


### only pricecomparison products

import re, sys, scrapy, urllib, urlparse

reload(sys)
sys.setdefaultencoding("utf-8")


class StackOverflowSpider(scrapy.Spider):
    name = 'pricearea'
    start_urls = ['http://www.pricearea.com/']
    allowed_domains = ['www.pricearea.com']

    def parse(self, response):  # goes through category table and clicks on every link in there
        ###All Categories:
        for cat in response.css('div.nav > ul.nav > li')[1:-1]:
            for href in cat.css('ul ul > li a::attr(href)'):
                url = response.urljoin(href.extract())
                yield scrapy.Request(url, callback=self.parse_category)

    def parse_category(self,
                       response):  # goes through all products, checks if they are pricecomparison(.pricing) and the link doesn't lead to the merchants website(jump?) then clicks on it
        if response.css('.pricing'):  # all pricecomparison products
            for href in response.css('.pricing li > a::attr(href)'):
                url = response.urljoin(href.extract())
                if 'jump?' in url:
                    continue
                else:
                    yield scrapy.Request(url, callback=self.parse_product)

    def parse_product(self, response):  # collects data from the product website
        name = response.css('.pa-breadccrumb li:last-child span::text').extract()
        category = '/'.join(map(str, response.css('.pa-breadccrumb span::text').extract()[1:-1]))
        if response.css('.logo-cat'):
            for offer in response.css('.product-title + .row .row'):  # price comparison list
                try:
                    merchant = offer.css('.logo-cat img::attr(alt)').extract()[0]
                    if len(merchant) == 0:
                        continue
                except IndexError:
                    continue
                try:
                    price = re.sub("[^0-9]", "", str(offer.css('.price-cat > h4::text').extract()))
                except IndexError:
                    price = 'not found'
                try:
                    merchantUrl = offer.css('.penjual a::attr(href)').extract()
                except IndexError:
                    merchantUrl = 'not found'
                yield {
                    'product name': name,
                    'category': category,
                    'merchant': merchant,
                    'price at this merchant': price,
                    'merchantUrl': merchantUrl,
                }
        else:  # no price comparison list?
            pass
