# coding=utf-8
# scrapy runspider pricebook-id.py -o pricebook-id.csv

import re, requests, sys, scrapy, urlparse

reload(sys)
sys.setdefaultencoding("utf-8")


class StackOverflowSpider(
    scrapy.spiders.SitemapSpider):  # sitemap spider (check out http://www.pricebook.co.id/sitemap_shop.xml)
    name = 'pricebook-id'

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    }

    sitemap_urls = ["http://www.pricebook.co.id/sitemap_shop.xml"]

    def parse(self, response):  # go to merchants page
        if len(response.css(".jump-last a::attr(href)").extract()) > 0:
            url = response.css(".jump-last a::attr(href)").extract()[0]
        else:
            url = response.url
        request = scrapy.Request(url, callback=self.parse_products)
        yield request

    def parse_products(self, response):  # collect information
        merchant = (response.css('.breadcrumb li:last-child span::text').extract()[0]).strip()
        products = (response.css('.pb-pricelist-list tr th:first-child::text').extract()[-1]).strip()
        yield {
            'domain': urlparse.urlparse(response.url).netloc,
            'path': urlparse.urlparse(response.url).path,
            'merchant': merchant,
            'products': products,
        }
