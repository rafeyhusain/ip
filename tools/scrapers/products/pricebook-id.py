# coding=utf-8
# scrapy runspider pricebook-id.py -o pricebook-id.csv

# only pricecomparison products

import re, sys, scrapy, urllib, urlparse

reload(sys)
sys.setdefaultencoding("utf-8")


class StackOverflowSpider(scrapy.Spider):
    name = 'pricebook-id'
    start_urls = ['http://www.pricebook.co.id/']
    allowed_domains = ['www.pricebook.co.id']

    def parse(self, response):  # looks at the category table and clicks on the links to the subcats
        ###All Categories:
        for cat in response.css('.nav-down ul> li:first-child ul > li'):
            for href in cat.css('ul > li a::attr(href)'):
                url = response.urljoin(href.extract())
                yield scrapy.Request(url, callback=self.parse_category)

    def parse_category(self, response):  # looks at each product and clicks on the link
        for href in response.css('.wrapper_tittle a::attr(href)'):
            url = response.urljoin(href.extract())
            request = scrapy.Request(url, callback=self.parse_merchant)
            yield request

        # if there is more than one product page it clicks on the link to the next page and recalls this function
        allLinks = response.css('.pagination-number > li')
        activeLink = response.css('.pagination-number > li.active')

        if len(allLinks) > 0:
            if allLinks[-1].xpath('@class').extract() != ['active']:
                sibling = allLinks.css('.active + li')
                url = response.urljoin(sibling.css('a::attr(href)').extract()[0])
                yield scrapy.Request(url, callback=self.parse_category)

    def parse_merchant(self, response):  # collects the data from the product website
        try:
            name = response.css('.inner-prod-name h2::text').extract()[0]
        except IndexError:
            name = 'not found'
        try:
            price = re.sub("[^0-9]", "", str(response.css('.pr-on strong::text').extract()[0]))
        except IndexError:
            price = 'not found'
        try:
            price_unit = str(response.css('.pr-on strong::text').extract()[0])[0:2]
        except IndexError:
            price_unit = 'not found'
        try:
            category = '/'.join(map(str, response.css('.breadcrumb li a > span::text').extract()))
        except IndexError:
            category = 'not found'
        try:
            reviews = response.css('.rating-info li > a span::text').extract()[0]
        except IndexError:
            reviews = 'not found'
        try:
            threads = response.css('.rating-info a[data-track-label="forum"] span::text').extract()[0]
        except IndexError:
            threads = 'not found'
        try:
            video = response.css('#video #player')
            video = 'yes'
        except IndexError:
            video = 'no'
        try:
            specs = response.css('#specification .section')
            specs = 'yes'
        except IndexError:
            specs = 'no'
        i = 0
        if len(response.css('.pb-pricelist-list > div')) > 0:
            # collects the data from the pricecomparison list but cannot load more than 10 merchants
            for offer in response.css('.pb-pricelist-list > div'):
                if offer.css('.ads-landscape'):
                    continue
                try:
                    merchant = (offer.css('.header_shop_list ul > li div a::text').extract()[0]).strip()
                except IndexError:
                    merchant = 'not found'
                try:
                    number_of_rates = re.sub("[^0-9]", "", (offer.css('.text-muted::text').extract()[0]).strip())
                except IndexError:
                    number_of_rates = 'unknown'
                try:
                    rating = offer.css('.header_shop_list .media-bodys li + li div::attr(data-rating)').extract()[0]
                except IndexError:
                    rating = 'unknown'
                try:
                    price_merchant = re.sub("[^0-9]", "", (offer.css('.price_list_shop ::text').extract()[1]).strip())
                except IndexError:
                    price_merchant = 'not found'
                try:
                    merchant_website = offer.css('.action_shop_list a::attr(href)').extract()[0]
                except IndexError:
                    merchant_website = 'not found'
                i += 1

                yield {
                    'specs': specs,
                    'video': video,
                    'threads': threads,
                    'url': response.url,
                    'product_name': name,
                    'price (on top of website)': price,
                    'price_unit': price_unit,
                    'category': category,
                    'user reviews': reviews,
                    'merchant': merchant,
                    'position of merchant for this product': i,
                    'number_of_rates for this merchant': number_of_rates,
                    'rating of this merchant': rating,
                    'price at this merchant': price_merchant,
                    'merchant_website': merchant_website,
                }
        else:  # no pricecomparison list
            merchant = 'not found'
            number_of_rates = 'not found'
            rating = 'not found'
            price_merchant = 'not found'
            merchant_website = 'not found'
            yield {
                'specs': specs,
                'video': video,
                'threads': threads,
                'url': response.url,
                'product_name': name,
                'price (on top of website)': price,
                'price_unit': price_unit,
                'category': category,
                'user reviews': reviews,
                'merchant': merchant,
                'position of merchant for this product': i,
                'number_of_rates for this merchant': number_of_rates,
                'rating of this merchant': rating,
                'price at this merchant': price_merchant,
                'merchant_website': merchant_website,
            }
