import scrapy
from selenium import webdriver
from scrapy.http import HtmlResponse
from scrapy.utils.python import to_bytes

# Test
from scrapy_selenium import SeleniumRequest

class MySpider(scrapy.Spider):
    name = 'adidas_spider'
    start_urls = ['https://www.adidas.es/hombre?grid=true',
                  'https://www.adidas.es/mujer?grid=true',
                  'https://www.adidas.es/ninos?grid=true']

    def start_requests(self):
        for url in self.start_urls:
            yield SeleniumRequest(url=url, callback=self.parse)

    def parse(self, response):
        # Use Scrapy selectors to extract data from the page
        pass