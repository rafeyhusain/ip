# coding=utf-8
# scrapy runspider pricearea.py -o pricearea.csv > priceareaprint.log

import re, requests, sys, scrapy, urlparse

reload(sys)
sys.setdefaultencoding("utf-8")


class StackOverflowSpider(
    scrapy.spiders.SitemapSpider):  # sitemap spider (check out www.pricearea.com/robots.txt and look for the sitemap with the merchants/shops)
    name = 'pricearea'

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    }

    sitemap_urls = [
        "http://www.pricearea.com/sitemap2015/sitemap-merchant.xml"]  # sitemap with the links, spider starts for every link on this page, check out one of these pages to see the structure

    def parse(self,
              response):  # on the merchant page try to find the number of products they have and the name of the merchant, so go to last page of the products and calculate 24*(number of pages)
        if response.css('.pagination'):
            allLinks = response.css('.pagination > li')
            if allLinks[-1].xpath('@class').extract() != ['active']:
                url = response.css('.pagination li > a::attr(href)').extract()[-2]
                yield scrapy.Request(url, callback=self.parse)
            else:
                merchant = (response.css('.pa-breadccrumb li:last-child a span::text').extract()[0]).strip()
                products = 24 * int(response.css('.pagination li a::text').extract()[-2])
                yield {
                    'domain': urlparse.urlparse(response.url).netloc,
                    'path': urlparse.urlparse(response.url).path,
                    'products': products,
                    'merchant': merchant,
                }
        else:
            merchant = response.css('.pa-breadccrumb li:last-child span::text').extract()[0]
            if response.css('.boxproductresult .price a::attr(href)'):
                products = len(response.css('.boxproductresult .price a::attr(href)').extract())
            else:
                products = 0
            yield {
                'domain': urlparse.urlparse(response.url).netloc,
                'path': urlparse.urlparse(response.url).path,
                'merchant': merchant,
                'products': products,
            }
