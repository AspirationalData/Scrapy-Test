# Scrapy-Test
Web Crawling Test using Scrapy


In order to build the scraper, we need to consider the following elements:

* Framework used (in our case, we'll use Scrapy).
* Site(s) that we wish to scrape (in our case, https://www.adidas.es/)
* Data to be scraped

    We wish to scrape the following information:

    * **Product title.**

        On the product page, we'll find the data using the following CSS selector:

        `response.css('h1.name___120FN span::text' ).get()`
        
    * **Product brand.**

        On the product page, we'll find the data using the following contant value:

        `Adidas`

        As every product is branded as "Adidas", this value is a constant.

    * **Product description.**

        On the product page, we'll find the data using the following CSS selector:

        `response.css('div.text-content___13aRm p::text').get()`

        (This selector needs to be modified)

        For this to work, we need to click to activate the dropdown, otherwise the product description does not show up.

        See Github Issue:
        https://github.com/clemfromspace/scrapy-selenium/issues/85

    * **Product current price.**

        On the product page, we'll find the data using the following code (it includes CSS selector):

        `current_product_prices_array = response.xpath('//*[@id="main-content"]/div/div[1]/div[2]/div/div/div').xpath('string()').get().replace('€', '').strip().split()`
        
        `float(current_product_prices_array[0]) if len(current_product_prices_array) == 1 else sorted(list(map(lambda x: float(x.replace(',', '.')), current_product_prices_array)))[0]`



    * **Product original price.**

        On the product page, we'll find the data using the following code (it includes CSS selector):

        `current_product_prices_array = response.xpath('//*[@id="main-content"]/div/div[1]/div[2]/div/div/div').xpath('string()').get().replace('€', '').strip().split()`

        `float(current_product_prices_array[0]) if len(current_product_prices_array) == 1 else sorted(list(map(lambda x: float(x.replace(',', '.')), current_product_prices_array)))[1]`


    * **Product availability.**

        On the product page, we'll find the data using the following code (it includes CSS selector):

        `available_sizes = response.css('div.sizes___2jQjF > button.gl-label.size___2lbev:not([class*="unavailable"]):not([class*="unavailable-crossed"]) > span::text').getall()`

        `bool(available_sizes)`


    * **A list of all the image URLs.**

        On the product page, we'll find the data using the following code (it includes CSS selector):

        `product_images = response.css('picture[data-testid="pdp-gallery-picture"] img').xpath('@src').extract()`

        `list(filter(lambda x: 'http' in x, product_images))`


    * **A unique Identifier for each product (SKU).**

        On the product page, we'll find the data using the following code (it includes CSS selector):

        `list(map(lambda href: href.split('/')[-1].replace('.html', ''), response.css('.slider___3D6S9 a::attr(href)').getall()))`

        The unique identifier changes for each "variation" of the product.


    * **All available colors for the product.**

        On the product page, we'll find the data using the following code (it includes CSS selector):

        `available_colors = response.css('div.slider___3D6S9 img::attr(alt)').getall()`

        `list(map(lambda x: x.replace("Color del artículo: ", ""), available_colors))`


    * **All available sizes for the product.**

        On the product page, we'll find the data using the following CSS selector:

        `response.css('.gl-label.size___2lbev span::text').getall()`


    * **Category paths leading to the product (e.g. Women > Footwear > Running).**

        On the product page, we'll find the data using the following code (it includes CSS selector):

        `[s for s in response.css('ol[data-auto-id="breadcrumbs-mobile"] span:not([aria-hidden="true"])::text').getall() if "Atrás" not in s and s != "/"]`

        The output needs some cleaning, as there are duplicates in the results.



## Middleware:

In order to be able to scrape the "Adidas" site, we needed to Modify the default Middleware used to scrape the website, as the website contains elements in the DOM that are not loaded by the default "Scrapy" middleware, since those elements are loaded dynamically using JS and the default middleware cannot run JS (those elements are lazy loaded, so the default middleware scraper is not able to "see" those elements in the DOM).

Therefore, we had to use the "selenium-scrapy-middleware", which can be installed by running the following command:


    `pip install scrapy_selenium`


When we run the scraper, given that you already modified the environmental variables in `settings.py` to point to the right WebDriver location on your local system (by default, it uses ChromeDriver), you can run the scraper by running the following command in the "scrapy-test" folder:


    `scrapy crawl adidas_spider`


## Scrapy project, inner workings.

Let's give a general overview of how the following Scrapy project works:

* **Start_url:**

    The inital URLs from which the scraper will start scraping are defined in this variable, so Scrapy will take the values in the iterable as a starting point to kick off the scraper.

* **Start_requests:**

    For each "starting" URL provided to the parameter above, it will open the website and call the "parse" method (defined on the next step).

* **Parse:**

    Does the actual parsing on the HTML DOM.

    Here, you'll be able to see and configure the elements that you want to scrape, and you'll be able to "get" those elements by using selectors (like the `CSS selector` or the `XPATH selector`, for instance) and the `yield` keyword.

    For example, you can select the data from a dictionary and save it on a dictionary-like structure (JSON object) using a chunk of code akin to the following one:

        `yield {
                    'text': quote.css('span.text::text').get(),
                    'author': quote.css('small.author::text').get(),
                    'tags': quote.css('div.tags a.tag::text').getall(),
                }`


    If you want to keep following link from the current site, you can use this chunk of code as a "starting point" to define how to keep following links:

        `next_page = response.css('li.next a::attr(href)').get()

            if next_page is not None:
                next_page = response.urljoin(next_page)
                yield SeleniumRequest(next_page, callback=self.parse)`


    The code defined above extract a URL and passes it again to the "Parse" method, calling it recursively to keep crawling data.


## Requirements

You can install all the requirements for this scraping project by running the following command.

    `pip install -r requirements.txt`



## Complementary project: FastAPI Data Consumption API

In order to complement this project, I created an API to be able to consume the information that is scraped using this Scrapy project.

You'll find the project on the following repository:

https://github.com/AspirationalData/FastAPI-Consumption-Endpoint