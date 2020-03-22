import scrapy
from scrapy.crawler import CrawlerProcess
from os import listdir
from os.path import isfile, join
import csv
import json
import datetime

class PostcodesMapper(scrapy.Spider):
    # spider name
    name = 'postcodes_mapper'
    
    # headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
    }
    
    # store mappings
    mapped = []
    
    def __init__(self):
        # get postcode files
        self.postcodes = [f for f in listdir('CSV') if isfile(join('CSV', f))]

        # loop over postcode files
        for postcode in self.postcodes:
            with open('./CSV/' + postcode, 'r') as csv_file:
                reader = csv.reader(csv_file)
                
                prev = ''
                
                # append results to mapped
                for line in reader:
                    try:
                        # extract outcodes
                        if len(line[0]) > 4:
                            current = line[0][0:3]
                        else:
                            current = line[0].split()[0]
                        
                        if current != prev:
                            prev = current
                        
                            self.mapped.append({
                                'postcode': current,
                                'locationId': ''
                            })

                    except:
                        # only ONE result fails because of malformed column
                        pass

    def start_requests(self):
        # loop over postcodes
        for item in self.mapped:
            url = 'https://www.rightmove.co.uk/commercial-property-for-sale/search.html?searchLocation=%s&useLocationIdentifier=false&locationIdentifier=&buy.x=SALE&search=For+Sale' % item['postcode']
            yield scrapy.Request(url=url, headers=self.headers, callback=self.parse, meta={'postcode': item['postcode']})
            #break
    
    def parse(self, res):
        # extract postcode and locId
        loc_id = res.css('input[id=locationIdentifier]::attr(value)').get()
        postcode = res.meta.get('postcode')
        
        # map postcode to locId
        for item in self.mapped:
            if postcode == item['postcode']:
                item['locationId'] = loc_id
    
    def write_results(self):
        with open('postcodes.json', 'w') as json_file:
            json_file.write(json.dumps(self.mapped, indent=2))
        

# run scrper
process = CrawlerProcess()
process.crawl(PostcodesMapper)
process.start()

# write results
PostcodesMapper.write_results(PostcodesMapper)
