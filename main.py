"""
Main module with some base analysis

Provides:
getLinks() to aggregating flats links from cian web-site
getLinksFromFile() for getting flats data from previously generated links file
parseData(links) for base parsing, gets 'links' dict as input

Author: Elizaveta Eskova
"""

# Import modules:
#- Requests module
#- csv module
#- parsers.csv
#- Beautiful Soup for pulling data out of HTML file
#- re module for providing regular expression
import requests
import csv
import parsers
from bs4 import BeautifulSoup
import re


# Base URL with needed string modificators
url = 'http://www.cian.ru/cat.php?deal_type=sale&district[0]=%s&engine_version=2&offer_type=flat&p=%s&room1=%s&room2=%s&room3=%s&room4=%s&room5=%s&room6=%s'

# Aggregate flat links from cian web-site
def getLinks():
    links = []
    prevLen = 0

    # Go through all the districts
    for dist in range(1, 348):
        
        # An array where the place of 1 indicates how many rooms in the flat
        for room in range(0, 6):
            a = []
            for j in range(0, room):
                a.append(0)
            a.append(1)
            for j in range(room+1, 6):
                a.append(0)

            # 30 pages with flats
            for page in range(1, 31):
                # The first '%s' in the url is a district, the second is a page number, and the rest are the array specifying the number of rooms
                page_url = url % tuple([dist, page] + a)
                # Get the content from url and pull the data
                search_page = requests.get(page_url).content
                search_page = BeautifulSoup(search_page, 'lxml')
                
                # Pull links from the page
                flat_urls = search_page.findAll('div', {'ng-class':"{'serp-item_removed': offer.remove.state, 'serp-item_popup-opened': isPopupOpen}"})
                flat_urls = re.split('http://www.cian.ru/sale/flat/|/" ng-class="', str(flat_urls))

                for link in flat_urls:
                    if link.isdigit() and not link in links:
                            links.append(link) #Add the flat index to the array
                print 'Page ' + str(page) + ', room ' + str(room) + ', region ' + str(dist) + ' finished, ' + str(len(links)) + ' links collected' # Going on output
                if len(links) == prevLen: #If we got a non-unique link, while the page count was less than 30, we started iterating again, so break
                    break
                prevLen = len(links)

    # Write the resulting flat numbers to file
    csvfile = open('/Users/anton/work/projects/cian/results/links.csv', 'wb')
    linkswriter = csv.writer(csvfile, delimiter=';', quotechar=';', quoting=csv.QUOTE_MINIMAL)
    linkswriter.writerow(links)
    csvfile.close()

    return links

# Get flats data from previously generated links file
def getLinksFromFile():
    links = []

    # Filename
    csvfile = open('/Users/anton/work/projects/cian/results/links.csv', 'rb')
    reader = csv.reader(csvfile, delimiter=';', quotechar=';', quoting=csv.QUOTE_MINIMAL)
    for link in reader:
        links.append(link)
    csvfile.close()

    # While we have some data - use it
    if len(links) > 0:
        return links[0]
    else:
        return []

# Parse data from generated links
def parseData(links):
    data = []

    # Checking if we have some data already
    csvfile = open('/Users/anton/work/projects/cian/results/pars.csv', 'rb')
    reader = csv.reader(csvfile, delimiter=';', quotechar=';', quoting=csv.QUOTE_MINIMAL)
    for row in reader:
        data.append(row)
    csvfile.close()

    # Putting data back
    csvfile = open('/Users/anton/work/projects/cian/results/pars.csv', 'wb')
    flatwriter = csv.writer(csvfile, delimiter=';', quotechar=';', quoting=csv.QUOTE_MINIMAL)
    if len(data) > 0:
        for row in data:
            flatwriter.writerow(row)
    else:
        flatwriter.writerow(['N', 'Rooms', 'Price', 'Totsp', 'Livesp', 'Kitsp', 'Dist', 'Metrdist', 'Walk', 'Brick', 'Tel', 'Bal', 'Floor', 'Nfloors', 'New'])

    # Generating new data from web-site
    for number in range(len(data)-2 if len(data) > 1 else 0, len(links)-1):
        def parseLinkData():
            page = links[number+1]
            print 'Flat ' + str(number+2) + '/' + str(len(links)) + ' ' + str(page)
            flat_url = 'http://www.cian.ru/sale/flat/' + str(page) + '/'
            data = BeautifulSoup(requests.get(flat_url).content, 'lxml')
            res = dict(parsers.pars(data).items() + {'N':str(page)}.items())
            print res
            return res

        def writeLinkData2CSV(res):
            flatwriter.writerow([
                res['N'],
                res['Rooms'],
                res['Price'],
                res['Totsp'],
                res['Livesp'],
                res['Kitsp'],
                res['Dist'],
                res['Metrdist'],
                res['Walk'],
                res['Brick'],
                res['Tel'],
                res['Bal'],
                res['Floor'],
                res['Nfloors'],
                res['New']
            ])

        # Broken pipe hotfix: don't write broken or bad uploaded pages
        for iteration in range(0, 10):
            res = parseLinkData()
            if res['Price'] != '-':
                writeLinkData2CSV(res)
                break

    csvfile.close()

# Requiring parsing from web-site or data-file
#parseData(getLinks())
parseData(getLinksFromFile())
