# coding=utf-8
# scrapy runspider websosanh.py -o websosanh.csv

import re, requests, sys, scrapy

reload(sys)
sys.setdefaultencoding("utf-8")


class StackOverflowSpider(scrapy.Spider):
    name = 'websosanh'
    start_urls = ['https://m.websosanh.vn/']

    def parse(self, response):
        for href in response.css('.menu-res a::attr(href)'):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_category)

    def parse_category(self, response):
        page = int(response.css('.paging .current::text').extract()[0])
        i = 0
        for item in response.css('.product-item'):
            i = i + 1

            url = response.urljoin(item.css('h3 a::attr(href)').extract()[0])
            url = url.replace("https://m.websosanh.vn", "https://websosanh.vn")

            if "so-sanh.htm" in url:
                request = scrapy.Request(url, callback=self.parse_product)
                request.meta['rank'] = i * page
                yield request

        next_page = response.css('link[rel="next"]::attr(href)')
        if len(next_page) > 0:
            url = next_page[0].extract()
            yield scrapy.Request(url, callback=self.parse_category)

    def parse_product(self, response):
        category = response.css('.breadcrumbs li:nth-child(3) a::text').extract()[0]
        name = response.css('h1::text').extract()[0]

        try:
            specs = response.css('#anchorProperties').extract()[0]
            specs = True
        except IndexError:
            specs = False

        try:
            comments = len(response.css('#listComment .media').extract())
        except IndexError:
            comments = 0

        i = 0
        for offer in response.css('#anchorComparePrice .line-solid:not(.hidden)'):

            i = i + 1
            merchant = offer.css('.col-merchant img::attr(src)').extract()[0].split("/")[-1].split(".")[0],
            price = re.sub("[^0-9]", "", "".join(offer.css('.col-price .price').extract()[0])),

            try:
                reputation = offer.css('.reputation').extract()[0]
                reputation = "trusted"
            except IndexError:
                reputation = "no"

            yield {
                'url': response.url,
                'category': category,
                'product': name,
                'rank': response.meta['rank'],
                'reviews': "n/a",
                'threads': comments,
                'news': "n/a",
                'specs': specs,
                'videos': "n/a",
                'description': "n/a",
                'position': i,
                'merchant': merchant,
                'price': price,
                'referral': reputation,
            }
