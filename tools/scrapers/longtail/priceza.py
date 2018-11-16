# coding=utf-8
# scrapy runspider priceza.py -o priceza.csv
import re, sys

reload(sys)
sys.setdefaultencoding("utf-8")

import scrapy


class StackOverflowSpider(scrapy.Spider):
    name = 'priceza'
    start_urls = ['http://www.priceza.com.my/keyword?page=2215&category=0&sort=0']

    def parse(self, response):
        for item in response.css('#content-keywords .tag'):

            try:
                yield {
                    'name': item.css('a::text').extract()[0],
                }
            except Exception, e:
                pass

        next_page = response.css('div.paging a.next::attr(href)')
        if len(next_page) > 0:
            full_url = response.urljoin(next_page[0].extract())
            yield scrapy.Request(full_url, callback=self.parse)
