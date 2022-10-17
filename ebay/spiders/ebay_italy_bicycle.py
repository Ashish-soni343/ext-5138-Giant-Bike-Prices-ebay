import scrapy
import datetime

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ..items import EbayItem

class EbayItalyBicycleSpider(CrawlSpider):
    name = 'ebay_italy_bicycle'
    start_urls = ["https://www.ebay.it/sch/177831/i.html?_from=R40&_nkw=giant+Biciclette&_sop=10&_ipg=240",]

    # Mandatory data
    #AEID_project_id = ''
    type = "Bicycle"
    site = 'www.ebay.it'
    source_country = 'Italy'
    context_identifier = ''
    item_ranking = 0
    #file_create_dt = datetime.datetime.utcnow().strftime('%Y-%m-%d %T')[0:10]
    record_created_by = ""
    execution_id = "622154"                # This will be taken automatically from zyte, for now this is hardcoded
    feed_code = "AEID-5183"


    # settings for Crawling
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'CONCURRENT_REQUESTS': 20,
        'COOKIES_ENABLED': True,
        'COOKIES_DEBUG': True,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 200,
        'DOWNLOAD_DELAY': 0,
        'AUTOTHROTTLE_ENABLED': False,
        'DOWNLOAD_TIMEOUT': 20,
        'DUPEFILTER_DEBUG': True,
        }

    rules = (
        Rule(LinkExtractor(restrict_css='.pagination__next', deny='_pgn=1')),
        Rule(LinkExtractor(restrict_css='a.s-item__link'), callback='parse_element_detail'),
    )


    def parse_element_detail(self, response):          # Function to extract data from fetched urls

        self.item_ranking += 1
        item = EbayItem()               # object to store data in "items.py"

        element = (response.css("#LeftSummaryPanel .ux-textspans--BOLD::text").get())
        Breads = response.css('li a.seo-breadcrumb-text span').css('::text').extract()
        if len(Breads) != 0:
            self.context_identifier = ""
        try:
            for bread in Breads:
                self.context_identifier = self.context_identifier + '>' + bread
                self.context_identifier = self.context_identifier.strip(">")
                self.type = bread
        except:
            pass

        specification_u = response.css(".ux-layout-section--features .ux-textspans::text").extract()
        key_value = ["Condition:", "Model Year:", "Shifter Style:", "Handlebar Type:", "Number of Speeds:", "Color:", "Wheel Size:", "Suspension Type:", "Bike Type:", "Brand:",
                        "Frame Size:", "Material:", "Department:", "Model:", "Brake Type:", "Tire Type:", "MPN:", "Vintage", "Gear Change Mechanism", "UPC", "Frame Number",
                     "Features", "Item Weight", "Stem", "Saddle", "Drivetrain Type", "Seatpost", "Gender", "Crankset", "Chainrings",
                     "Cassette", "Wheel Set", "Front Derailleur", "Fork", "Rear Derailleur", "Shifters"]
        key_value_lang = ["Condizione:", "Jahr:", "Shifter Style:", "Lenkerart:", "Numero di cambi", "Colore principale:", "Wheel Size:", "Federung:", "Tipo:", "Marca:",
                          "Dimensioni telaio:", "Materiale telaio:", "Abteilung:", "Modell:", "Tipo di freno:", "Reifentyp:", "MPN:", "Vintage", "Gear Change Mechanism", "UPC", "Frame Number",
                          "Features", "Item Weight", "Stem", "Saddle", "Drivetrain Type", "Seatpost", "Genere:", "Crankset", "Chainrings", "Cassette", "Wheel Set",
                          "Front Derailleur", "Fork", "Rear Derailleur", "Shifters"]
        for key in key_value:
            item[key.replace(" ", "_").replace(":", "")] = ""

        item["Age_in_years"] = ""

        for i in range(len(specification_u)-1):
            for (j, k) in zip(key_value, key_value_lang):
                if ":" in specification_u[i + 1] and i >= 3:
                    break
                if "Mostra di più" in specification_u[i]:
                    item["Condition"] = specification_u[i + 1]
                if "Colour" in specification_u[i]:
                    item["Color"] = specification_u[i + 1]
                if "Marke:" in specification_u[i]:
                    item["Brand"] = specification_u[i + 1]

                if k in specification_u[i] or j in specification_u[i]:
                    item[j.replace(" ", "_").replace(":", "")] = specification_u[i + 1]

                try:
                    if "Model Year" in specification_u[i] or "Jahr" in specification_u[i]:
                        date = datetime.date.today()
                        current_year = date.year

                        item["Age_in_years"] = (current_year) - int(specification_u[i + 1])
                except:
                    item["Age_in_years"] = ""


        self.record_created_by = self.name
        #self.execution_id = "something"#environ.get('SHUB_JOBKEY', None)

        # Data scraped
        item["record_create_dt"] = datetime.datetime.utcnow().strftime('%Y-%m-%d %T')
        item["type"] = self.type
        item["title"] = element
        titles = response.css('.x-item-title__mainTitle').css('::text').extract()
        title_fix = ""
        try:
            for title in titles:
                title_fix = title_fix + title
            if len(item['title']) < len(title_fix):
                item['title'] = title_fix.rstrip('-')
            else:
                item['title'] = element.rstrip('-')
        except:
            pass
        item["currency"] = "EUR"
        #item["specs"] = specification_u
        if len(item["Condition"]) == 0:
            item["Condition"] = response.css(".ux-icon-text__text .ux-textspans").css('::text').extract()

        if len(response.css("#prcIsum::text").extract()) != 0:

            item["price"] = str(response.css("#prcIsum::text").extract()).strip("['").strip("']")
            item["starting_bid"] = ""
            item["total_bid"] = ""

        elif len(response.css("#mm-saleDscPrc::text").extract()) != 0:

            item["price"] = str(response.css("#mm-saleDscPrc::text").extract()).strip("['").strip("']")
            item["starting_bid"] = ""
            item["total_bid"] = ""

        else:

            item["price"] = ""
            item["starting_bid"] = ""
            item["total_bid"] = ""

        if len(response.css("#prcIsum_bidPrice.notranslate::text").extract()) != 0:  # or response.css("#prcIsum_bidPrice.notranslate::text").extract() != "" :

            item["starting_bid"] = str(response.css("#prcIsum_bidPrice.notranslate::text").extract()).strip("['").strip("']")
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




