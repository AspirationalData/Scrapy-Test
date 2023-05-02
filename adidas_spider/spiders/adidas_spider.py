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

        # response.css('.glass-product-card__assets')
        # response.css('.glass-product-card__assets a::attr(href)').extract()
        # response.css('.glass-product-card-container.with-variation-carousel')
        for entry in response.css('.glass-product-card__assets a::attr(href)').extract():
            yield SeleniumRequest(url=str('https://www.adidas.es/' + entry), callback=self.parse)

            # For every page, parse colors, size, etc.
            for entry in response.css('div.slider___3D6S9').extract():
                yield {
                    'Colors': response.css('div.slider___3D6S9 img::attr(alt)').getall()
                }

        

        # Navigator bar 'universal' class: gl-vspace color-chooser-draggable-bar___ZqytD
        # Sub-slider class: slider___3D6S9



        ### ELEMENTS ###
        # Breadcrumbs div class: breadcrumb_item___32Yik

        # Colors (selects especific color, does not generalize):
        # Link: https://www.adidas.es/zapatilla-forum-low-cl-x-indigo-herz/IE1855.html
        # response.css('.variation___u2aRL.selected___1f4ky.variation-selected__color___2zTSy img::attr(alt)').getall()


        


        # Scrapy, follow next pages example
        """
        class QuotesSpider(scrapy.Spider):
        name = "quotes"
        start_urls = [
            'https://quotes.toscrape.com/page/1/',
        ]

        def parse(self, response):
            for quote in response.css('div.quote'):
                yield {
                    'text': quote.css('span.text::text').get(),
                    'author': quote.css('small.author::text').get(),
                    'tags': quote.css('div.tags a.tag::text').getall(),
                }

            next_page = response.css('li.next a::attr(href)').get()
            if next_page is not None:
                next_page = response.urljoin(next_page)
                yield scrapy.Request(next_page, callback=self.parse)
            
        """