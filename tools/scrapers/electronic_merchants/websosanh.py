# coding=utf-8
# scrapy runspider websosanh.py -o websosanh.csv

import re, requests, sys, scrapy

reload(sys)
sys.setdefaultencoding("utf-8")


class StackOverflowSpider(scrapy.Spider):
    name = 'websosanh'
    start_urls = ['https://websosanh.vn/']
    categories = ['/dien-thoai-may-tinh-bang/', '/tivi-am-thanh/', '/thiet-bi-gia-dung/', '/dien-lanh/',
                  '/may-anh-may-quay-phim/', '/thiet-bi-van-phong/', '/thiet-bi-sieu-thi/', '/tin-hoc/']
    currency = 'VND'
    country = 'Vietnam'

    def parse(self, response):
        for href in response.css('.dropdown-menu a::attr(href)'):
            url = response.urljoin(href.extract())
            if (max(list(map(lambda x: x in url, self.categories)))):
                yield scrapy.Request(url, callback=self.parse_category)

    def parse_category(self, response):
        for item in response.css('.item'):
            url = response.urljoin(item.css('h3 a::attr(href)').extract()[0])

            if "so-sanh.htm" in url:
                request = scrapy.Request(url, callback=self.parse_product)
                yield request

        next_page = response.css('.pagination .next::attr(data-page-index)').extract()[0]
        if len(next_page) > 0:
            url = re.sub("\?.*", "", response.url) + "?pi=" + next_page + ".htm"
            yield scrapy.Request(url, callback=self.parse_category)

    def parse_product(self, response):
        category = response.css('.breadcrumbs li:nth-child(3) a::text').extract()[0]
        name = response.css('h1::text').extract()[0]

        i = 0
        for offer in response.css('#anchorComparePrice .line-solid:not(.hidden)'):
            merchant = offer.css('.rate::text').extract()[0]
            price = re.sub("[^0-9]", "", "".join(offer.css('.col-price .price').extract()[0]))
            yield {
                'url': response.url,
                'category': category,
                'product': name,
                'position': i,
                'merchant': merchant,
                'price': price,
                'currency': self.currency,
                'country': self.country
            }
            i = i + 1
