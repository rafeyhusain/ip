# coding=utf-8
# scrapy runspider priceprice.py -o priceprice.csv
# scrapy runspider priceprice.py -o priceprice.csv --logfile=priceprice.log > pricepriceprint.log

import re, sys, scrapy, urllib, urlparse

reload(sys)
sys.setdefaultencoding("utf-8")


class StackOverflowSpider(scrapy.Spider):
    name = 'priceprice'
    start_urls = ['http://ph.priceprice.com/', 'http://id.priceprice.com/', 'http://th.priceprice.com/']
    allowed_domains = ['ph.priceprice.com', 'id.priceprice.com', 'th.priceprice.com']

    def parse(self, response):  # goes to the category table and clicks on the links to the subcats
        for box in response.css('.topCatList > .topCatBox'):
            href = box.css('.topCatInfo > span > a::attr(href)')
            url = response.urljoin(href.extract()[0])
            yield scrapy.Request(url, callback=self.parse_category)

    def parse_category(self, response):
        if response.css('#itemList'):  # gets all categories but men's fashion, women's fashion and beauty
            if response.css(
                    '#itemList .catalogItem'):  # gets mobilephone accesories, computer accesories, lenses, camera accesories, tv audio and video accesories -> no price comparison
                for prod in response.css('#itemList .catalogItem'):
                    number_merchants = 1
                    category = (response.css('.breadcrumbs span::text').extract()[-1]).strip()
                    name = (prod.css('.catalogItemName::text').extract()[0]).strip()
                    reviews = 'not found'
                    threads = 'not found'
                    news = 'not found'
                    specs = 'not found'
                    videos = 'not found'
                    description = 'not found'
                    i = 'no pricecomparison'
                    try:
                        if len(prod.css('.shop::text').extract()) > 0:
                            merchant = prod.css('.shop::text').extract()
                        else:
                            merchant = 'not found'
                    except IndexError:
                        merchant = 'not found'
                    try:
                        price = re.sub("[^0-9]", "", prod.css('.catalogItemPrice::text').extract()[0])
                    except IndexError:
                        price = 'not found'
                    referral = 'not found'
                    yield {
                        'number of merchants': number_merchants,
                        'domain': urlparse.urlparse(response.url).netloc,
                        'path': urlparse.urlparse(response.url).path,
                        'category': category,
                        'product name': name,
                        'user reviews': reviews,
                        'threads': threads,
                        'news': news,
                        'specs': specs,
                        'videos': videos,
                        'description': description,
                        'rank of the merchant': i,
                        'merchant': merchant,
                        'price': price,
                        'referral': referral,
                    }
            else:  # pricecomparison pages
                if response.css('#itemList .itemBox'):  # not subcat of beauty
                    for item in response.css('#itemList .itemBox'):
                        url = response.urljoin(item.css('.itmName a::attr(href)').extract()[0])
                        yield scrapy.Request(url, callback=self.parse_product)
                else:
                    for item in response.css('#itemList .item'):  # subcats of beauty
                        url = response.urljoin(item.css('p.name a::attr(href)').extract()[0])
                        yield scrapy.Request(url, callback=self.parse_product)

            # more than one page of products: clicks on link to next page
            if response.css('.pagenation .last a::attr(href)'):
                url = response.urljoin(response.css('.pagenation .last a::attr(href)').extract()[0])
                yield scrapy.Request(url, callback=self.parse_category)
            elif response.css('.pagination .next a::attr(href)'):
                url = response.urljoin(response.css('.pagination .next a::attr(href)').extract()[0])
                yield scrapy.Request(url, callback=self.parse_category)
        else:  # gets men's fashion, women's fashion and beauty, goes to subcategories
            for cat in response.css('ul.cat > li'):
                url = response.urljoin(cat.css('div > a::attr(href)').extract()[0])
                yield scrapy.Request(url, callback=self.parse_fashion)

    def parse_fashion(self, response):  # collects the data from the productpage for fashion
        if response.css('#itemList'):  # makeup has pricecomparison
            yield scrapy.Request(response.url, callback=self.parse_category)
        else:
            for prod in response.css('.itemArea .item'):
                number_merchants = 1
                category = '/'.join(map(str, response.css('.breadcrumb span::text').extract()[1:-1]))
                name = prod.css('p.name::text').extract()[0]
                reviews = 'not found'
                threads = 'not found'
                news = 'not found'
                specs = 'not found'
                videos = 'not found'
                description = 'not found'
                i = 'no pricecomparison'
                try:
                    merchant = prod.css('p.shop::text').extract()
                except IndexError:
                    merchant = 'not found'
                try:
                    price = re.sub("[^0-9]", "", prod.css('.catalogItemPrice::text').extract()[0])
                except IndexError:
                    price = 'not found'
                referral = 'not found'
                yield {
                    'number of merchants': number_merchants,
                    'domain': urlparse.urlparse(response.url).netloc,
                    'path': urlparse.urlparse(response.url).path,
                    'category': category,
                    'product name': name,
                    'user reviews': reviews,
                    'threads': threads,
                    'news': news,
                    'specs': specs,
                    'videos': videos,
                    'description': description,
                    'rank of the merchant': i,
                    'merchant': merchant,
                    'price': price,
                    'referral': referral,
                }

    def parse_product(self, response):  # collects the data from the product pages that have pricecomparison
        category = '/'.join(filter(None, map(unicode.strip, response.css('.breadcrumbs li ::text').extract()[1:-1])))
        if len(response.css('.breadcrumbs li:last-child ::text').extract()[0]) > 0:
            name = response.css('.breadcrumbs li:last-child ::text').extract()[0]
        else:
            name = response.css('.breadcrumbs li:last-child span::text').extract()[0]
        try:
            if response.css('#prclst span::text'):
                number_merchants = re.sub("[^0-9]", "", str(response.css('#prclst span::text').extract()[0]))
            else:
                number_merchants = re.sub("[^0-9]", "", str(response.css('.page-section p::text').extract()[0]))
        except IndexError:
            number_merchants = 'not found'
        try:
            reviews = re.sub("[^0-9]", "", str(response.css('.summaryRating h3 span > span::text').extract()))
        except IndexError:
            reviews = 'not found'
        try:
            threads = len(response.css('.summaryForum > .forumBox'))
        except IndexError:
            threads = 'not found'
        try:
            news = response.css('.summaryBox .latestNews').extract()[0]
            news = 'yes'
        except IndexError:
            news = 'no'
        try:
            specs = response.css('.summaryBox .summarySpec').extract()[0]
            specs = 'yes'
        except IndexError:
            specs = 'no'
        try:
            videos = response.css('.summaryBox .summaryVideo').extract()[0]
            videos = 'yes'
        except IndexError:
            videos = 'no'
        try:
            description = response.css('.summaryBox .summaryDescript').extract()[0]
            description = 'yes'
        except IndexError:
            description = 'no'

        i = 0

        if response.css('.itemBox'):  # loops through the merchant in the pricecomparison list
            for offer in response.css('.itemBox'):
                try:
                    if offer.css('div.itmShop img::attr(alt)'):
                        merchant = offer.css('div.itmShop img::attr(alt)').extract()[0]
                    else:
                        merchant = offer.css('div.itmShop > div > a > span::text').extract()[0]
                except IndexError:
                    merchant = 'not found'
                try:
                    referral = offer.css('div.itmBtn > .shopBtn01::attr(href)').extract()[0]
                    referral = urllib.unquote(referral.replace('/jump/shop/?url=', ""))
                except IndexError:
                    referral = "offline"
                try:
                    price = re.sub("[^0-9]", "", offer.css('p.price::text').extract()[0])
                except IndexError:
                    price = 'not found'
                i = i + 1
                yield {
                    'number of merchants': number_merchants,
                    'domain': urlparse.urlparse(response.url).netloc,
                    'path': urlparse.urlparse(response.url).path,
                    'category': category,
                    'product name': name,
                    'user reviews': reviews,
                    'threads': threads,
                    'news': news,
                    'specs': specs,
                    'videos': videos,
                    'description': description,
                    'rank of the merchant': i,
                    'merchant': merchant,
                    'price': price,
                    'referral': referral,
                }

        else:  # not more than one merchant
            merchant = 'not found'
            referral = 'not found'
            i = 'no merchants found'
            try:
                price = re.sub("[^0-9]", "", response.css('span.price::text').extract()[0])
            except IndexError:
                price = 'not found'
            yield {
                'number of merchants': number_merchants,
                'domain': urlparse.urlparse(response.url).netloc,
                'path': urlparse.urlparse(response.url).path,
                'category': category,
                'product name': name,
                'user reviews': reviews,
                'threads': threads,
                'news': news,
                'specs': specs,
                'videos': videos,
                'description': description,
                'rank of the merchant': i,
                'merchant': merchant,
                'price': price,
                'referral': referral,
            }
