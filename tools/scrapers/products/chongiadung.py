# coding=utf-8
# scrapy runspider websosanh.py -o websosanh.csv

import re, requests, sys, scrapy

reload(sys)
sys.setdefaultencoding("utf-8")


class StackOverflowSpider(scrapy.Spider):
    name = 'websosanh'
    start_urls = ['http://www.chongiadung.com/danh-muc-mua-sam.html']

    def parse(self, response):
        for href in response.css('.parent-nav > a::attr(href)'):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_category)

    def parse_category(self, response):

        page = int(re.sub("[^0-9]", "", response.css('.pagination .active a::text').extract()[0]))
        i = 0
        for item in response.css('.prItem'):
            i = i + 1

            prices = item.css('.prShopBlock span strong::text').extract()

            if len(prices) > 1:
                prices = int(re.sub("[^0-9]", "", prices[1]))
            else:
                prices = 0

            if prices > 1:
                url = response.urljoin(item.css('a::attr(href)').extract()[0])

                request = scrapy.Request(url, callback=self.parse_product)
                request.meta['rank'] = i * page
                yield request

        next_page = response.css('.pagination .next a::attr(href)')
        if len(next_page) > 0:
            url = next_page[0].extract()
            yield scrapy.Request(url, callback=self.parse_category)

    def parse_product(self, response):
        category = response.css('.breadcrumb li:nth-child(2) a::text').extract()[0]
        name = response.css('.breadcrumb li:last-child h2::text').extract()[0]

        try:
            specs = response.css('#property').extract()[0]
            specs = True
        except IndexError:
            specs = False

        try:
            description = len(response.css('#description').extract())
        except IndexError:
            description = 0

        i = 0
        for offer in response.css('.shopList .divTableRow:not(.trChild)'):

            i = i + 1

            try:
                merchant = offer.css('.shopNameTxt::text').extract()[0].strip()
                referral = "basic"
            except IndexError:
                merchant = offer.css('.shopNameImg img::attr(alt)').extract()[0]
                referral = "image"

            price = re.sub("[^0-9]", "", "".join(offer.css('.priceShop').extract()[0])),

            yield {
                'url': response.url,
                'category': category,
                'product': name,
                'rank': response.meta['rank'],
                'reviews': "n/a",
                'threads': "facebook",
                'news': "n/a",
                'specs': specs,
                'videos': "n/a",
                'description': description,
                'position': i,
                'merchant': merchant,
                'price': price,
                'referral': referral,
            }
