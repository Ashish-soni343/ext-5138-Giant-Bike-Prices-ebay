import scrapy
import datetime

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ..items import EbayItem

class CarDekhoSpider(CrawlSpider):

    name = 'giant_bicycles'
    #start_urls = ["https://www.ebay.com/sch/i.html?_from=R40&_nkw=giant+bike&_sacat=0&_sop=10&_ipg=60", "https://www.ebay.com/sch/i.html?_from=R40&_nkw=giant+bike&_sacat=0&_sop=10&_ipg=60&_pgn=2", "https://www.ebay.com/sch/i.html?_from=R40&_nkw=giant+bike&_sacat=0&_sop=10&_ipg=60&_pgn=3", "https://www.ebay.com/sch/i.html?_from=R40&_nkw=giant+bike&_sacat=0&_sop=10&_ipg=60&_pgn=4"]
    #start_urls = ["https://www.ebay.com/sch/i.html?_from=R40&_nkw=Giant+Bicycles&_sacat=0&_ipg=240"]
    #start_urls = ["https://www.ebay.com/sch/i.html?_from=R40&_nkw=Giant+Bicycles&_sacat=0&_ipg=60"]
    start_urls = ["https://www.ebay.com/sch/i.html?_from=R40&_nkw=Giant+Bike&_sacat=0&_ipg=240"]

    # Mandatory data
    #AEID_project_id = ''
    type = "Bicycles"
    site = 'www.ebay.com'
    source_country = 'US'
    context_identifier = ''
    item_ranking = 1
    #file_create_dt = datetime.datetime.utcnow().strftime('%Y-%m-%d %T')[0:10]
    record_created_by = ""
    execution_id = ""                # This will be taken automatically from zyte, for now this is hardcoded
    feed_code = "12345"


    # settings for Crawling
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'CONCURRENT_REQUESTS': 20,
        'COOKIES_ENABLED': True,
        'COOKIES_DEBUG': True,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 500,
        'DOWNLOAD_DELAY': 2,
        "DOWNLOADER_MIDDLEWARES": {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,
        },
        "AUTOTHROTTLE_ENABLED": False,
        "DOWNLOAD_TIMEOUT": 20,
        }

    rules = (
        Rule(LinkExtractor(allow='itm'), callback='parse_element_detail'),
    )

    def parse_elements(self, response):           # funtion to fetch url for each car

        elements = response.css('a.s-item__link::attr(href)').extract()

        for element in elements:
            yield response.follow(
                url=element,
                callback=self.parse_element_detail
            )
            #self.item_ranking += 1


    def parse_element_detail(self, response):          # Function to extract data from fetched urls

        #print(response.url)

        item = EbayItem()               # object to store data in "items.py"
        #print("response============", response.json)

        element = (response.css("#LeftSummaryPanel .ux-textspans--BOLD::text").get())
        self.context_identifier = (response.css("a.seo-breadcrumb-text span::text").extract()) + list(">") + (response.css("a[aria-current='location'] span::text").extract())
        specification_u = response.css(".ux-layout-section--features .ux-textspans::text").extract()
        #specification = json.dumps(specification_u)
        key_value = ["Condition:", "Model Year:", "Shifter Style:", "Handlebar Type:", "Number of Speeds:", "Color:", "Wheel Size:", "Suspension Type:", "Bike Type:", "Brand:",
                        "Frame Size:", "Material:", "Department:", "Model:", "Brake Type:", "Tire Type:", "MPN:"]
        for key in key_value:
            item[key.replace(" ", "_").replace(":", "")] = ""

        for i in range(len(specification_u)) :
            for j in key_value:

                if j in specification_u[i]:
                    item[j.replace(" ", "_").replace(":", "")] = specification_u[i + 1]
                if "Read more" in specification_u[i]:
                    item["Condition"] = specification_u[i + 1]


        self.record_created_by = self.name
        self.execution_id = "something"#environ.get('SHUB_JOBKEY', None)
        """if item["Model_Year"] != "" or item["Model_Year"] !=[]:
            date = datetime.date.today()
            current_year = date.year
            print("item year", item["Model_Year"])

            item["Age"] = int(current_year) - int(item["Model_Year"])"""

        # Data scraped
        item["record_create_dt"] = datetime.datetime.utcnow().strftime('%Y-%m-%d %T')
        item["type"] = self.type
        item["element"] = element
        item["currency"] = "US Dollar"

        if len(response.css("#prcIsum_bidPrice.notranslate::text").extract()) != 0 : #or response.css("#prcIsum_bidPrice.notranslate::text").extract() != "" :

            item["starting_bid"] = response.css("#prcIsum_bidPrice.notranslate::text").extract()
            item["total_bid"] = response.css("#qty-test::text").get()
            item["price"] = ""

        elif response.css("#prcIsum::text").extract() !=0:

            item["price"] = response.css("#prcIsum::text").extract()
            item["starting_bid"] = ""
            item["total_bid"] = ""

        else:

            item["price"] = response.css("# mm-saleDscPrc::text").extract()
            item["starting_bid"] = ""
            item["total_bid"] = ""
        item["feed_code"] = self.feed_code
        item["site"] = self.site
        item["source_country"] = self.source_country
        item["context_identifier"] = self.context_identifier
        item["record_create_by"] = self.record_created_by
        #item["execution_id"] = self.execution_id
        item["item_ranking"] = self.item_ranking
        #item["specification"] = specification
        item["src"] = response.url

        yield item
        self.item_ranking += 1


