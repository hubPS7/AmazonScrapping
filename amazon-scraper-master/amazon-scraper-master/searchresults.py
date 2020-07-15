from selectorlib import Extractor
import requests
import csv
from quantulum3 import parser
#import json
#from time import sleep

# Create an Extractor by reading from the YAML file
e = Extractor.from_yaml_file('search_results.yml')

def scrape(url):  

    headers = {
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://www.amazon.com/',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    }

    # Download the page using requests
    # print("Downloading %s"%url)
    r = requests.get(url, headers=headers)
    # Simple check to check if page was blocked (Usually 503)
    if r.status_code > 500:
        if "To discuss automated access to Amazon data please contact" in r.text:
            print("Page %s was blocked by Amazon. Please try using better proxies\n" % url)
        else:
            print("Page %s must have been blocked by Amazon as the status code was %d" % (url, r.status_code))
        return None
    # Pass the HTML of the page and create
    return e.extract(r.text)

fields = ['title', 'url', 'rating', 'reviews', 'price', 'quantity', 'productName']
out_file = open('./Organic.csv', 'w', encoding='utf-8')
csvwriter = csv.DictWriter(out_file, delimiter=',', fieldnames=fields)
csvwriter.writeheader()

page_number = 1
service_count = 1

while True:
    # Check if reached end of result
    if page_number > 10:
        break
    #for url in urllist.read().splitlines():
    url = "https://www.amazon.in/s?k=organic&rh=p_72%3A1318476031&dc&page=" + str(page_number)
    print(url)
    data = scrape(url)
    if data:
        for product in data['products']:
            dict_service = {}

            product['search_url'] = url
            title = product['title']
            url = product['url']
            rating = product['rating']
            reviews = product['reviews']
            priceList = str(product['price']).split('₹')
            if(priceList.__len__() > 1):
                price = priceList[1]
            else:
                price = product['price']


            #Product Quantity fetching
            listQuantity = parser.parse(title)
            if(listQuantity.__len__() > 0):
                quantity = listQuantity[0].surface
            else:
                quantity = ''

            #Product name fetching
            listProduct = title.split(' ')
            if (listProduct.__len__() > 0):
                productName = listProduct[0] + ' ' + listProduct[1]

            dict_service['title'] = title
            dict_service['url'] = url
            dict_service['rating'] = rating
            dict_service['reviews'] = reviews
            dict_service['price'] = price
            dict_service['quantity'] = quantity
            dict_service['productName'] = productName

            print("Saving Product: %s"%product['title'])
            #json.dump(product,outfile)
            #outfile.write("\n")

            # Write row to CSV
            csvwriter.writerow(dict_service)

            print("#" + str(service_count) + " ", dict_service)
            service_count += 1
            #sleep(5)

    page_number += 1
out_file.close()