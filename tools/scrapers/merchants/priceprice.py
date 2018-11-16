# coding=utf-8
# scrapy runspider priceprice.py -o priceprice.csv

import re, requests, sys, scrapy, urlparse

reload(sys)
sys.setdefaultencoding("utf-8")


class StackOverflowSpider(
    scrapy.spiders.SitemapSpider):  # sitemap spider, check out http://ph.priceprice.com/sitemap_shop.xml
    name = 'priceza'

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    }

    sitemap_urls = ["http://ph.priceprice.com/sitemap_shop.xml", "http://id.priceprice.com/sitemap_shop.xml",
                    "http://th.priceprice.com/sitemap_shop.xml"]

    def parse(self, response):  # go to merchants page

        url = response.urljoin("products/")
        request = scrapy.Request(url, callback=self.parse_products)
        yield request

    def parse_products(self, response):  # collect the information
        merchant = response.css('.info .name::text').extract()[0]
        location = response.css('.info .type::text').extract()[0].strip("\n")

        products = response.css('.navArea ul li span em::text').extract()[0]

        yield {
            'domain': urlparse.urlparse(response.url).netloc,
            'path': urlparse.urlparse(response.url).path,
            'merchant': merchant,
            'location': location,
            'products': products,
        }
