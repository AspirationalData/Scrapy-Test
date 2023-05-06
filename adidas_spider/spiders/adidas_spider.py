import scrapy
from selenium import webdriver
import time

from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class MySpider(scrapy.Spider):

    """
    Class that defines the spider.
    """

    # Max wait time when trying to load a page
    DOWNLOAD_TIMEOUT = 45


    name = 'adidas_spider'

    base_url = 'https://www.adidas.es'

    start_urls = ['https://www.adidas.es/hombre?grid=true',
                  'https://www.adidas.es/mujer?grid=true',
                  'https://www.adidas.es/ninos?grid=true']
    
    
    def __init__(self, *args, **kwargs):
        super(MySpider, self).__init__(*args, **kwargs)
        self.driver = webdriver.Chrome(executable_path='/Users/joel/Downloads/chromedriver_mac_arm64/chromedriver')


    def start_requests(self):
        for url in self.start_urls:
            yield SeleniumRequest(url=url,
                                  callback=self.parse_product_directories,
                                  wait_until=EC.element_to_be_clickable((By.ID, 'glass-gdpr-default-consent-accept-button')),
                                  script="document.querySelector('#glass-gdpr-default-consent-accept-button').click();",
                                  meta={'driver': self.driver}
                                 )
    

    def parse_product_directories(self, response):

        """
        Parses product pagers and follows the link for each product on the page.

        After following each and every product and doing the parsing,
        it goes to the next page.
        """
        
        for product_url in response.css('.glass-product-card__assets a::attr(href)').extract():
            yield SeleniumRequest(url=self.base_url + product_url,
                                  callback=self.parse,
                                  meta={'driver': self.driver})
            
            # Checks if there are more pages avaiable and, if so, follows
            # the link to the next page until there are not any more
            # pages to crawl
            next_page = response.css('.pagination__control___3C268.pagination__control--next___329Qo.pagination_margin--next___3H3Zd a::attr(href)').get()
            if next_page is not None:
                next_page = self.base_url + next_page
                yield SeleniumRequest(url=next_page, callback=self.parse_product_directories)

        
        
    def parse(self, response):

        """
        Parses product information from product pages.
        """

        # Click on the button before using CSS selectors.
        # This will allow us to extract the Description.

        # driver = response.request.meta.get('driver')
        # print('Driver:', driver)
        driver = response.meta['driver']

        
        # The idea here is to wait for the GDPR cookie banner to appear and click on "Accept Cookies"
        # try:
            # button = driver.find_element(By.ID, 'glass-gdpr-default-consent-accept-button')
            # button = WebDriverWait(driver=driver, timeout=10).until(EC.presence_of_element_located((By.ID, 'glass-gdpr-default-consent-accept-button')))
            # button.click()
        
        # WebDriver timeout exception
        # except Exception:
        #     pass

        

        # Click on Description dropdown.
        try:
            # button = driver.find_element(By.CSS_SELECTOR, 'button.accordion__header___3Pii5')
            description_slider_button_xpath = '/html/body/div[2]/div/div[1]/div[1]/div/div/div[4]/div/div[3]/section[3]/div/div/button'
            # description_slider_button_xpath = '//*[@id="navigation-target-description"]/div/button'
            # button = WebDriverWait(driver=driver, timeout=10).until(EC.element_to_be_clickable((By.XPATH, description_slider_button_xpath)))
            element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, description_slider_button_xpath)))

            # Re-parse page source to scrape the items.


            # Click on the element
            driver.execute_script("arguments[0].click();", element)


            # button.click()
            # time.sleep(5)

        # WebDriver timeout exception
        except Exception:
            pass

        
        # Variable that shows Current Price and Original Price.
        current_product_prices_array = response.xpath('//*[@id="main-content"]/div/div[1]/div[2]/div/div/div').xpath('string()').get().replace('€', '').strip().split()

        # List of images of page product (of the product itself).
        product_images = response.css('picture[data-testid="pdp-gallery-picture"] img').xpath('@src').extract()

        # Available colors list.
        available_colors = response.css('div.slider___3D6S9 img::attr(alt)').getall()

        # Available sizes list.
        available_sizes = response.css('div.sizes___2jQjF > button.gl-label.size___2lbev:not([class*="unavailable"]):not([class*="unavailable-crossed"]) > span::text').getall()

        yield {
            
            # Extract product title:
            'Product Title': response.css('.name___120FN span::text').get(),

            # Extract product brand:
            'Product Brand': 'Adidas',

            # Extract product description:
            # View issue:
            # https://github.com/clemfromspace/scrapy-selenium/issues/85
            # 'Product Description': ' '.join(response.css('div.text-content___13aRm h3, div.text-content___13aRm p::text').getall()),
            'Product Description': response.css('div.text-content___13aRm p::text').get(),
            # p::text


            
            # Current Product price extraction logic:

            # First, extracts the product price array (1 item if there's no discount),
            # 2 items if it's discounted.
            # If the list length is 2, grabs the lowest number.
            # This assumes the price with the lowest value is the Current Price.

            
            # Extract product current price:
            'Current Price': float(current_product_prices_array[0]) if len(current_product_prices_array) == 1 else sorted(list(map(lambda x: float(x.replace(',', '.')), current_product_prices_array)))[0],

            # Extract product original price:
            'Original Price': float(current_product_prices_array[0]) if len(current_product_prices_array) == 1 else sorted(list(map(lambda x: float(x.replace(',', '.')), current_product_prices_array)))[1],

            # From the product where you can select a size, says "True" if there is at least
            # one size available.
            # If the product does not have sizes, it says "One-size-fits-all Product"
            # Extract product availability:
            'Product Availability': bool(available_sizes),

            # We'll extract all the link of the PRODUCT ITSELF.
            # Extract all image URLs (of said product) from the product page:
            'Image URLs': list(filter(lambda x: 'http' in x, product_images)),
            
            # All SKUs are present in the product page URL at the end.
            # Extract all SKUs:
            'SKUs': list(map(lambda href: href.split('/')[-1].replace('.html', ''), response.css('.slider___3D6S9 a::attr(href)').getall())),


            # Extract available colors. 
            'Available Colors': list(map(lambda x: x.replace("Color del artículo: ", ""), available_colors)),

            # Extract all available sizes:
            'Available Sizes': available_sizes,

            # Extract breadcrumbs:
            'Breadcrumbs': [s for s in response.css('ol[data-auto-id="breadcrumbs-mobile"] span:not([aria-hidden="true"])::text').getall() if "Atrás" not in s and s != "/"]
            
        }



        # Navigator bar 'universal' class: gl-vspace color-chooser-draggable-bar___ZqytD
        # Sub-slider class: slider___3D6S9



        ### ELEMENTS ###
        # Breadcrumbs div class: breadcrumb_item___32Yik

        # Colors (selects especific color, does not generalize):
        # Link: https://www.adidas.es/zapatilla-forum-low-cl-x-indigo-herz/IE1855.html
        # response.css('.variation___u2aRL.selected___1f4ky.variation-selected__color___2zTSy img::attr(alt)').getall()
