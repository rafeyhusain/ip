# coding=utf-8
# scrapy runspider price-hk.py -o price-hk.csv

import re, sys, scrapy, urllib, urlparse

reload(sys)
sys.setdefaultencoding("utf-8")


# only pricecomparison

class StackOverflowSpider(scrapy.Spider):
    name = 'price-hk'
    start_urls = ['http://price.com.hk/']
    allowed_domains = ['www.price.com.hk']

    def parse(self, response):  # takes the links for the categories and clicks on them
        ###All Categories:
        for href in response.css('div.menu-mega ul > li a::attr(href)'):
            ###Top Categories:
            # for href in response.css('div.menu-mega ul > li .column-left a::attr(href)'):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_category)

    def parse_category(self, response):  # takes links for the products and clicks on them
        for href in response.css('ul.list-product-list .item .column-02 > .line-01 a::attr(href)'):
            url = response.urljoin(href.extract())
            # set cookies for english
            request = scrapy.Request(url, cookies={'ui_lang_pref': 'en_US'}, callback=self.parse_merchant)
            yield request

        # if there is more than one product page it goes to the next page and recalls this function
        allLinks = response.css('.pagination > li')
        # activeLink = response.css('.pagination > li.active')

        if len(allLinks) > 0:
            if allLinks[-1].xpath('@class').extract() != ['active']:
                sibling = allLinks.css('.active + li')
                url = response.urljoin(sibling.css('a::attr(href)').extract()[0])
                yield scrapy.Request(url, callback=self.parse_category)

    def parse_merchant(self, response):  # collects the data from the productpage
        try:
            name = response.css('div.product-col-info h1.product-name::text').extract()[0]
        except IndexError:
            name = 'not found'
        try:
            price = response.css('div.product-col-info span.product-price ::text').extract()[1]
        except IndexError:
            price = 'not found'
        try:
            price_unit = response.css('div.product-col-info span.product-price ::text').extract()[0]
        except IndexError:
            price_unit = 'not found'
        try:
            category = '/'.join(map(str, response.css('.breadcrumb-product a::text').extract()[1:-1]))
        except IndexError:
            category = 'not found'
        try:
            reviews = re.sub("[^0-9]", "", str(response.css('ul.list-inline .active + li a::text').extract()))
        except IndexError:
            reviews = 'not found'
        if response.css('.line-06 td') != []:
            description = 'description found'
        else:
            description = 'no description'

        i = 0

        for offer in response.css(
                'div.page-product > ul > li'):  # goes through the price comparison list and collects more data
            if offer.css('::attr(id)'):
                try:
                    merchant = offer.css('.quotation-merchant-name ::text').extract()[0]
                except IndexError:
                    merchant = 'not found'
            else:
                merchant = 'False; maybe advertisement'
            try:
                number_of_orders = offer.css('div.column-01 div.quotation-merchant-spec-total p::text').extract()[1]
            except IndexError:
                number_of_orders = 'unkown'
            try:
                number_of_rates = offer.css('div.column-01 div.quotation-merchant-spec-rating p::text').extract()[0]
            except IndexError:
                number_of_rates = 'unknown'
            try:
                rating = re.sub("[^0-9]", "",
                                offer.css('div.column-01 div.quotation-merchant-spec-rating img::attr(src)').extract()[
                                    0])
            except IndexError:
                rating = 'unknown'
            try:
                price_green = offer.css('div.column-03 div.quote-price-hong span.product-price ::text').extract()[1]
            except IndexError:
                price_green = 'not found'
            try:
                price_blue = offer.css('div.column-03 div.quote-price-water span.product-price ::text').extract()[1]
            except IndexError:
                price_blue = 'not found'
            try:
                merchant_website = offer.css('.column-03 .refer-btn-detail a::attr(title)').extract()[0]
                if merchant_website != 'Order through Price':
                    merchant_website = offer.css(
                        'div.column-03 div.price-refer-btn div.refer-btn-detail a::attr(href)').extract()
            except IndexError:
                merchant_website = 'not found'
            try:
                merchant_online = (offer.css('.quotation-merchant-level + a::text').extract()[0]).strip()
            except IndexError:
                merchant_online = 'unknown'
            i += 1

            yield {
                'url': response.url,
                'product_name': name,
                'price (on top of website)': price,
                'price_unit': price_unit,
                'category': category,
                'description': description,
                'user reviews': reviews,
                'merchant': merchant,
                'position of merchant for this product': i,
                'number_of_orders through this merchant': number_of_orders,
                'number_of_rates for this merchant': number_of_rates,
                'rating of this merchant': rating,
                'price_merchant (Dealer Good)': price_green,
                'price unconfirmed (Grey Import)': price_blue,
                'merchant_website': merchant_website,
                'merchant_online': merchant_online,
            }

        # if there is more than one page in the pricecomparison list it clicks on the next page and recalls the function
        allLinks = response.css('ul.pagination > li')
        # activeLink = response.css('ul.pagination > li.active')

        if len(allLinks) > 0:
            if allLinks[-1].xpath('@class').extract() != ['active']:
                sibling = allLinks.css('.active + li')
                url = response.urljoin(sibling.css('a::attr(href)').extract()[0])
                yield scrapy.Request(url, callback=self.parse_merchant)
