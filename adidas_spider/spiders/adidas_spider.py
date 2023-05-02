import scrapy
from selenium import webdriver
from scrapy.http import HtmlResponse
from scrapy.utils.python import to_bytes

from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC



class MySpider(scrapy.Spider):

    """
    Class that defines the spider.
    """


    name = 'adidas_spider'

    base_url = 'https://www.adidas.es'

    start_urls = ['https://www.adidas.es/hombre?grid=true',
                  'https://www.adidas.es/mujer?grid=true',
                  'https://www.adidas.es/ninos?grid=true']

    def start_requests(self):
        for url in self.start_urls:
            yield SeleniumRequest(url=url,
                                  callback=self.parse_product_pages,
                                  wait_until=EC.element_to_be_clickable((By.ID, 'glass-gdpr-default-consent-accept-button')),
                                  script="document.querySelector('#glass-gdpr-default-consent-accept-button').click();"
                                 )
    

    def parse_product_pages(self, response):

        """
        Parses product pagers and follows the link for each product on the page.

        After following each and every product and doing the parsing,
        it goes to the next page.
        """
        
        for product_url in response.css('.glass-product-card__assets a::attr(href)').extract():
            yield SeleniumRequest(url= self.base_url + product_url,
                                  callback=self.parse)
            
            # Checks if there are more pages avaiable and, if so, follows
            # the link to the next page until there are not any more
            # pages to crawl
            next_page = response.css('.pagination__control___3C268.pagination__control--next___329Qo.pagination_margin--next___3H3Zd a::attr(href)').get()
            if next_page is not None:
                next_page = self.base_url + next_page
                yield SeleniumRequest(next_page, callback=self.parse)

        
        
    def parse(self, response):

        """
        Parses product information from product pages.
        """


        yield {

            'Colors': response.css('div.slider___3D6S9 img::attr(alt)').getall(),

            # The available size CSS selector needs to be corrected, as it
            # not discard non-available items.

            # Alternative selector:
            # response.css('button.gl-label.size___2lbev:not(.size-selector__size--unavailable) span::text').getall()
            'Available sizes': response.css('.gl-label.size___2lbev span::text').getall(),

            # The following CSS selector is supposed to select all
            # colors, but for some reason it only selects one of them
            'Available colors': response.css('div.slider___3D6S9 img::attr(alt)').getall(),

            # Extract all SKUs:
            'SKUs': list(map(lambda href: href.split('/')[-1].replace('.html', ''), response.css('.slider___3D6S9 a::attr(href)').getall())),

            # Extract all image URLs from the product page:
            'Image URLs': response.css('img ::attr(src)').getall(),

            # Extract product current price:
            'Current Price': response.css('.gl-price-item.notranslate ::text').get(),

            # Extract product original price:
            'Original Price': response.css('.gl-price-item.notranslate ::text').get(),

            # Need to implement logic based on the number of items
            # under the div class "gl-price gl-price--horizontal notranslate"
            # 'Original Price': 

            # Extract product brand:
            'Product Brand': 'Adidas',

            # Extract product description:
            # View issue:
            # https://github.com/clemfromspace/scrapy-selenium/issues/85
            'Product Description': 'test',

            # Extract breadcrumbs:
            # Yields duplicate values, we'll figure out logic (on the CSS selector or
            # external logic) to deal with it.
            'Breadcrumbs': response.css('.breadcrumb_item___32Yik a span::text').getall()
        }



        # Navigator bar 'universal' class: gl-vspace color-chooser-draggable-bar___ZqytD
        # Sub-slider class: slider___3D6S9



        ### ELEMENTS ###
        # Breadcrumbs div class: breadcrumb_item___32Yik

        # Colors (selects especific color, does not generalize):
        # Link: https://www.adidas.es/zapatilla-forum-low-cl-x-indigo-herz/IE1855.html
        # response.css('.variation___u2aRL.selected___1f4ky.variation-selected__color___2zTSy img::attr(alt)').getall()
