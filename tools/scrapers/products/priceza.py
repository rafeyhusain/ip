# coding=utf-8
# scrapy runspider priceza.py -o priceza.csv
# scrapy runspider priceza.py -o priceza.csv --logfile=priceza.log > pricezaprint.log

import re, requests, sys, scrapy, urllib, urlparse

reload(sys)
sys.setdefaultencoding("utf-8")


class StackOverflowSpider(scrapy.Spider):
    name = 'priceza'
    start_urls = ['http://www.priceza.com', 'http://www.priceza.com.my', 'http://www.priceza.co.id',
                  'http://www.priceza.com.sg', 'http://www.priceza.com.ph', 'http://www.priceza.com.vn']
    allowed_domains = ['www.priceza.com', 'www.priceza.com.my', 'www.priceza.co.id', 'www.priceza.com.sg',
                       'www.priceza.com.ph', 'www.priceza.com.vn']

    redirects = {}

    def parse(self, response):  # goes through the category table and clicks on the links to the maincats
        ###Top Categories:
        for href in response.css('.dropdown-menu ul > li a::attr(href)'):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_category)

    def parse_category(self, response):  # goes through the category table and clicks on the links to the subcats
        for href in response.css('.sub-cat-side ul > li ul > li a::attr(href)'):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_product)

    def parse_product(self,
                      response):  # goes through the products and collects data / clicks on the links to the product pages
        if response.css('.products .btn-compare'):  # check if pricecomparison products on this website
            for element in response.css('.products .grid-box'):
                if element.css('.goto-merchant'):  # link goes to merchant website, so collect data here
                    try:
                        name = element.css('.productdetail h3::text').extract()
                    except IndexError:
                        name = 'not found'
                    try:
                        category = '/'.join(map(str, response.css('div.bc-new > a::text').extract()))
                    except IndexError:
                        category = 'not found'
                    try:
                        price = element.css('.price span::attr(content)').extract()[1]
                    except IndexError:
                        price = 'not found'
                    try:
                        currency = element.css('.price span::attr(content)').extract()[0]
                    except IndexError:
                        currency = 'not found'
                    try:
                        merchant = element.css('.rating-merchant img::attr(alt)').extract()[0]
                    except IndexError:
                        merchant = 'not found'
                    try:
                        rating = re.sub("[^0-9]", "", str(element.css('.rate-star div::attr(style)').extract()[1]))
                    except IndexError:
                        rating = 'not found'
                    try:
                        if element.css('.pd-info > span::text').extract():
                            description = 'yes'
                        else:
                            description = 'no'
                    except IndexError:
                        description = 'not found'
                    payments = 'no pricecomparison'
                    reviews = 'no pricecomparison'
                    specs = 'no pricecomparison'
                    price_merchant = 'no pricecomparison'
                    position = 'no pricecomparison'
                    items = 'no pricecomparison'
                    yield {
                        'url': response.url,
                        'product name': name,
                        'category': category,
                        'price': price,
                        'user reviews': reviews,
                        'specifications': specs,
                        'description': description,
                        'more items at this merchant': items,
                        'currency': currency,
                        'merchant': merchant,
                        'payment options': payments,
                        'price at this merchant': price_merchant,
                        'rating of this merchant': rating,
                        'position of this merchant': position,
                    }
                elif element.css('.btn-compare'):  # clicks on link to the productwebsite with pricecomparison
                    if 'com.my' in response.url:
                        url = self.start_urls[1] + str(element.css('.info a::attr(href)').extract()[0])
                    elif 'co.id' in response.url:
                        url = self.start_urls[2] + str(element.css('.info a::attr(href)').extract()[0])
                    elif 'com/' in response.url:
                        url = self.start_urls[0] + str(element.css('.info a::attr(href)').extract()[0])
                    elif 'com.sg' in response.url:
                        url = self.start_urls[3] + str(element.css('.info a::attr(href)').extract()[0])
                    elif 'com.ph' in response.url:
                        url = self.start_urls[4] + str(element.css('.info a::attr(href)').extract()[0])
                    elif 'com.vn' in response.url:
                        url = self.start_urls[5] + str(element.css('.info a::attr(href)').extract()[0])
                    yield scrapy.Request(url, callback=self.parse_merchant)

            # if there is more than one product page, click on the link to the next page and recall this function
            allLinks = response.css('div.pagination > a')
            # activeLink = response.css('div.pagination > a.active')

            if len(allLinks) > 0:
                if allLinks[-1].xpath('@class').extract() != ['active']:
                    sibling = allLinks.css('.active + a')
                    url = response.urljoin(sibling.css('a::attr(href)').extract()[0])
                    yield scrapy.Request(url, callback=self.parse_product)

                    # nextpage = response.css('i.icon-pz-arrow-right < a::attr(href)').extract
                    # if nextpage != '#':
                    # url = response.urljoin(nextpage)
                    # yield scrapy.Request(url, callback=self.parse_product)

    def parse_merchant(self, response):  # collects data from productpage
        try:
            name = response.css('#summary > .info > h1 > span::text').extract()
        except IndexError:
            name = 'not found'
        try:
            category = '/'.join(map(str, response.css('.bc.hidden-xs a::text').extract()))
        except IndexError:
            category = 'not found'
        try:
            price = response.css('#summary > .info span.price::text').extract()
        except IndexError:
            price = 'not found'
        try:
            currency = response.css('#summary > .info span.price small::text').extract()
        except IndexError:
            currency = 'not found'
        try:
            reviews = re.sub("[^0-9]", "", str(response.css('.all-reviews h2 > small::text').extract()[0]))
        except IndexError:
            reviews = 'not found'
        try:
            if response.css('.detail-specificat > h2::text').extract():
                specs = 'yes'
            else:
                specs = 'no'
        except IndexError:
            specs = 'not found'
        try:
            if response.css('#summary .info-text::text').extract():
                description = 'yes'
            else:
                description = 'no'
        except IndexError:
            description = 'not found'
        i = 1
        if response.css(
                '#detail .seller'):  # loops through the merchant in the pricecomparison list and collects the data
            for seller in response.css('#detail .seller'):
                try:
                    merchant = seller.css('.info .brand a img::attr(alt)').extract()
                except IndexError:
                    merchant = 'not found'
                try:
                    price_merchant = seller.css('.col-md-3 .price a::text').extract()[1]
                except IndexError:
                    price_merchant = 'not found'
                try:
                    rating = re.sub("[^0-9]", "", seller.css('.stars-group div::attr(style)').extract()[0])
                except IndexError:
                    rating = 'not found'
                try:
                    payments = seller.css('.payments div > i::attr(title)').extract()
                except IndexError:
                    payments = 'not found'
                try:
                    if len(re.sub("[^0-9]", "", str(seller.css('.col-md-3 .price a + a::text').extract()))) > 0:
                        items = re.sub("[^0-9]", "", str(seller.css('.col-md-3 .price a + a::text').extract()))
                    else:
                        items = 'information not found'
                except IndexError:
                    items = 'information not found'
                yield {
                    'url': response.url,
                    'product name': name,
                    'category': category,
                    'price': price,
                    'user reviews': reviews,
                    'specifications': specs,
                    'description': description,
                    'more items at this merchant': items,
                    'currency': currency,
                    'merchant': merchant,
                    'payment options': payments,
                    'price at this merchant': price_merchant,
                    'rating of this merchant': rating,
                    'position of the merchant': i,
                }
                i += 1
        elif response.css('#detail .pg-seller__row'):  # for thai pages
            for seller in response.css('#detail .pg-seller__row'):
                try:
                    merchant = seller.css('.pg-seller__col--brand a img::attr(alt)').extract()
                except IndexError:
                    merchant = 'not found'
                try:
                    price_merchant = (seller.css('.pg-seller__col--price a + a::text').extract()[1]).strip()
                except IndexError:
                    price_merchant = 'not found'
                try:
                    rating = re.sub("[^0-9]", "", seller.css('.stars-group div::attr(style)').extract()[0])
                except IndexError:
                    rating = 'not found'
                try:
                    payments = []
                    for payment in seller.css('.pg-seller__col--payment div ::text').extract():
                        if len(payment.strip()) > 0:
                            payments.append(payment.strip())
                except IndexError:
                    payments = 'not found'
                try:
                    if len(re.sub("[^0-9]", "", str(seller.css('.col-md-3 .price a + a::text').extract()))) > 0:
                        items = re.sub("[^0-9]", "", str(seller.css('.col-md-3 .price a + a::text').extract()))
                    else:
                        items = 'information not found'
                except IndexError:
                    items = 'information not found'
                yield {
                    'url': response.url,
                    'product name': name,
                    'category': category,
                    'price': price,
                    'user reviews': reviews,
                    'specifications': specs,
                    'description': description,
                    'more items at this merchant': items,
                    'currency': currency,
                    'merchant': merchant,
                    'payment options': payments,
                    'price at this merchant': price_merchant,
                    'rating of this merchant': rating,
                    'position of the merchant': i,
                }
                i += 1
