from selectorlib import Extractor
import requests 
import json
import csv
from time import sleep


# Create an Extractor by reading from the YAML file
e = Extractor.from_yaml_file('search_results.yml')

fields = ['title', 'url', 'rating', 'reviews', 'price', 'quantity', 'productName']
out_file = open('../hardware.csv', 'w')
csvwriter = csv.DictWriter(out_file, delimiter=',', fieldnames=fields)

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

#product_data = []
with open("search_results_urls.txt",'r') as urllist, open('search_results_output.jsonl','w') as outfile:
    page_number = 1
    service_count = 1
    dict_service = {}
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

                product['search_url'] = url
                title = product['title']
                url = product['url']
                rating = product['rating']
                reviews = product['reviews']
                price = product['price']

                #Product Quantity fetching
                listQuantity = title.split(',')
                if(listQuantity.__len__() > 0):
                    quantity = listQuantity[listQuantity.__len__() - 1]

                if(quantity.__len__() > 7):
                    listQuantity = title.split(' ')
                if (listQuantity.__len__() > 0):
                    quantity = listQuantity[listQuantity.__len__() - 2] + listQuantity[listQuantity.__len__() - 1]

                if (quantity.__len__() > 7):
                    listQuantity = title.split('-')
                if (listQuantity.__len__() > 0):
                    quantity = listQuantity[listQuantity.__len__() - 1]

                if(quantity.endswith('ml') or quantity.endswith('gm') or quantity.endswith('gram') or quantity.endswith('l')
                or quantity.endswith('GM') or quantity.endswith('L') or quantity.endswith('litre') or quantity.endswith('LITRE')):
                    quantity = listQuantity[listQuantity.__len__() - 1]
                else:
                    quantity = ''

                for i in range(len(listQuantity)):
                    if(listQuantity[i] == 'ml' or  listQuantity[i] == 'ML'  or listQuantity[i] == 'gm' or listQuantity[i] =='gram' or listQuantity[i] == 'Gram'
                            or listQuantity[i] == 'GM' or listQuantity[i] == 'l' or listQuantity[i] == 'L' or listQuantity[i] == 'litre' or listQuantity[i] == 'Litre'):
                        quantity = listQuantity[i-1] = listQuantity[i]
                        break

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
                json.dump(product,outfile)
                outfile.write("\n")
                # Write row to CSV
                #csvwriter.writerow(dict_service)
                #sleep(5)

        page_number += 1
    