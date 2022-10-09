import scrapy
import datetime

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ..items import EbayItem

class CarDekhoSpider(CrawlSpider):

    name = 'giant_bikes'
    #start_urls = ["https://www.ebay.com/sch/i.html?_from=R40&_nkw=giant+bike&_sacat=0&_sop=10&_ipg=60", "https://www.ebay.com/sch/i.html?_from=R40&_nkw=giant+bike&_sacat=0&_sop=10&_ipg=60&_pgn=2", "https://www.ebay.com/sch/i.html?_from=R40&_nkw=giant+bike&_sacat=0&_sop=10&_ipg=60&_pgn=3", "https://www.ebay.com/sch/i.html?_from=R40&_nkw=giant+bike&_sacat=0&_sop=10&_ipg=60&_pgn=4"]
    start_urls = ["https://www.ebay.com/sch/i.html?_from=R40&_nkw=Giant+Bike&_sacat=0&_ipg=240"]
    #start_urls = ["https://www.ebay.com/sch/i.html?_from=R40&_nkw=giant+bike&_sacat=0&_sop=10&_ipg=60"]

    # Mandatory data
    #AEID_project_id = ''
    type = "Bike"
    site = 'www.ebay.com'
    source_country = 'US'
    context_identifier = ''
    item_ranking = 0
    #file_create_dt = datetime.datetime.utcnow().strftime('%Y-%m-%d %T')[0:10]
    record_created_by = ""
    execution_id = "622154"                # This will be taken automatically from zyte, for now this is hardcoded
    feed_code = "12345"


    # settings for Crawling
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'CONCURRENT_REQUESTS': 30,
        'COOKIES_ENABLED': True,
        'COOKIES_DEBUG': True,
        'SPIDERMON_ENABLED': True,
        'EXTENSIONS': {
            'spidermon.contrib.scrapy.extensions.Spidermon': 500,
            },
        'SPIDERMON_SPIDER_CLOSE_MONITORS': (
            'ebay.monitors.SpiderCloseMonitorSuite',
            ),
        'SPIDERMON_SLACK_SENDER_TOKEN': '<SLACK_SENDER_TOKEN>',
        'SPIDERMON_SLACK_SENDER_NAME': '<SLACK_SENDER_NAME>',
        'SPIDERMON_SLACK_RECIPIENTS': ['@yourself', '#yourprojectchannel'],
        "ITEM_PIPELINES": {
            'spidermon.contrib.scrapy.pipelines.ItemValidationPipeline': 800,
        },
        "SPIDERMON_VALIDATION_MODELS": (
            'ebay.validators.ProductItem',
        ),
        'CONCURRENT_REQUESTS_PER_DOMAIN': 500,
        'DOWNLOAD_DELAY': 0,
        'AUTOTHROTTLE_ENABLED': False,
        'DOWNLOAD_TIMEOUT': 20,
        'DUPEFILTER_DEBUG': True,
        }

    rules = (
        Rule(LinkExtractor(allow='itm'), callback='parse_element_detail'),
    )


    def parse_element_detail(self, response,):          # Function to extract data from fetched urls

        self.item_ranking += 1
        item = EbayItem()               # object to store data in "items.py"

        element = (response.css("#LeftSummaryPanel .ux-textspans--BOLD::text").get())
        Breads = response.css('li a.seo-breadcrumb-text span').css('::text').extract()
        self.context_identifier = ""
        try:
            for bread in Breads:
                self.context_identifier = self.context_identifier + '>' + bread
        except:
            pass

        specification_u = response.css(".ux-layout-section--features .ux-textspans::text").extract()
        key_value = ["Condition:", "Model Year:", "Shifter Style:", "Handlebar Type:", "Number of Speeds:", "Color:", "Wheel Size:", "Suspension Type:", "Bike Type:", "Brand:",
                        "Frame Size:", "Material:", "Department:", "Model:", "Brake Type:", "Tire Type:", "MPN:", "Vintage", "Gear Change Mechanism", "UPC", "Frame Number",
                     "Features", "Item Weight", "Stem", "Saddle", "Drivetrain Type", "Seatpost", "Gender", "Crankset", "Chainrings",
                     "Cassette", "Wheel Set", "Front Derailleur", "Fork", "Rear Derailleur", "Shifters"]
        for key in key_value:
            item[key.replace(" ", "_").replace(":", "")] = ""

        item["Age"] = ""

        for i in range(len(specification_u)-1):
            for j in key_value:
                if ":" in specification_u[i + 1]:
                    break

                if j in specification_u[i]:
                    item[j.replace(" ", "_").replace(":", "")] = specification_u[i + 1]
                if "Read more" in specification_u[i]:
                    item["Condition"] = specification_u[i + 1]
                try:
                    if "Model Year" in specification_u[i]:

                        date = datetime.date.today()
                        current_year = date.year

                        item["Age"] = str((current_year) - int(specification_u[i + 1]))
                except:
                    item["Age"] = ""


        self.record_created_by = self.name
        self.execution_id = "34210"   #environ.get('SHUB_JOBKEY', None)

        # Data scraped
        item["record_create_dt"] = datetime.datetime.utcnow().strftime('%Y-%m-%d %T')
        item["type"] = self.type
        item["title"] = element
        item["currency"] = "US Dollar"

        if len(response.css("#prcIsum::text").extract()) != 0:

            item["price"] = str(response.css("#prcIsum::text").extract())
            item["starting_bid"] = ""
            item["total_bid"] = ""

        elif len(response.css("#mm-saleDscPrc::text").extract()) != 0:

            item["price"] = str(response.css("#mm-saleDscPrc::text").extract())
            item["starting_bid"] = ""
            item["total_bid"] = ""

        else:

            item["price"] = ""
            item["starting_bid"] = ""
            item["total_bid"] = ""

        if len(response.css("#prcIsum_bidPrice.notranslate::text").extract()) != 0: #or response.css("#prcIsum_bidPrice.notranslate::text").extract() != "" :

            item["starting_bid"] = str(response.css("#prcIsum_bidPrice.notranslate::text").extract())
            item["total_bid"] = str(response.css("#qty-test::text").get())

        item["feed_code"] = self.feed_code
        item["site"] = self.site
        item["source_country"] = self.source_country
        item["context_identifier"] = self.context_identifier
        item["record_create_by"] = self.record_created_by
        item["execution_id"] = self.execution_id
        item["item_ranking"] = self.item_ranking
        #item["specification"] = specification
        item["src"] = response.url

        yield item

