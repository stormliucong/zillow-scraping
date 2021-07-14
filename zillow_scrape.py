
import urllib.request
import urllib.parse
import urllib.error
from bs4 import BeautifulSoup
import ssl
import json
import ast
import os
from urllib.request import Request, urlopen
import re

url = '''
https://www.zillow.com/pennington-nj/sold/3-_beds/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22usersSearchTerm%22%3A%22Pennington%2C%20NJ%22%2C%22mapBounds%22%3A%7B%22west%22%3A-74.95789158056643%2C%22east%22%3A-74.63860141943361%2C%22south%22%3A40.24489761028678%2C%22north%22%3A40.4171099973018%7D%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A6462%2C%22regionType%22%3A6%7D%5D%2C%22isMapVisible%22%3Atrue%2C%22filterState%22%3A%7B%22price%22%3A%7B%22min%22%3A0%2C%22max%22%3A700000%7D%2C%22mp%22%3A%7B%22min%22%3A0%2C%22max%22%3A2297%7D%2C%22beds%22%3A%7B%22min%22%3A3%7D%2C%22built%22%3A%7B%22min%22%3A1950%7D%2C%22ah%22%3A%7B%22value%22%3Atrue%7D%2C%22rs%22%3A%7B%22value%22%3Atrue%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%7D%2C%22isListVisible%22%3Atrue%2C%22mapZoom%22%3A12%7D
'''
url = '''
https://www.zillow.com/pennington-nj/sold/
'''
# url = '''

# '''

def url_generator(base_url):
    property_list = []
    i = 1
    while(i<=100):
        try:
            url = base_url.strip() + str(i) + '_p'
            print(url)
            property_list.extend(get_home_cards(url))
            i = i + 1
        except:
            break
    return property_list

# Making the website believe that you are accessing it using a mozilla browser
def get_home_cards(url):
    searched_link = {}
    # For ignoring SSL certificate errors
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    soup = BeautifulSoup(webpage, 'html.parser')
    html = soup.prettify('utf-8')
    with open('/Users/cl3720/Desktop/output_file.html', 'wb') as file:
        file.write(html)
    property_list = []
    for homelink in soup.findAll('a',attrs={'href':True}):
        link = homelink['href']
        m = re.match('.*https\:\/\/www.zillow\.com\/homedetails.*',link)
        if m:
            if link not in searched_link.keys():
                print(link)
                # property_list.append(get_url_details(link))
                # searched_link[link] = 1
    return property_list, html


def get_url_details(url):
    # For ignoring SSL certificate errors
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    # url = 'https://www.zillow.com/homedetails/305-Deer-Run-Ct-Pennington-NJ-08534/64525656_zpid/' # an example.
    headers = {
           'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
           'accept-encoding': 'gzip, deflate, br',
           'accept-language': 'en-US,en;q=0.8',
           'upgrade-insecure-requests': '1',
           'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
        }
    req = Request(url, headers=headers)
    webpage = urlopen(req).read()

    # Creating a BeautifulSoup object of the html page for easy extraction of data.

    soup = BeautifulSoup(webpage, 'html.parser')
    html = soup.prettify('utf-8')
    property_json = {}

    for title in soup.findAll('title'):
        property_json['Title'] = title.text.strip()
        break
    for meta in soup.findAll('meta', attrs={'name': 'description'}):
        property_json['Detail_Short'] = meta['content'].strip()

    for div in soup.findAll('div', attrs={'class': 'character-count-truncated'}):
        property_json['Description'] = div.text.strip()

    for span in soup.findAll('span',attrs={'class': 'fiSzLC'}):
        sold_date = span.text.strip()
        m = re.match('Sold on.+?(\d+\/\d+/\d+).*',sold_date)
        if m:
            property_json['Last_Sold_Date'] = m.group(1)
            break

    for span in soup.findAll('span',attrs={'class': 'zsg-icon-recently-sold'}):
        next_span = span.find_next_siblings('span')
        sold_price = span.text.strip()
        property_json['Last_Sold_Price'] = next_span[0].text.strip().replace(": ","")

        break

    for span in soup.findAll('span'):
        if span.text.strip() == 'Lot:':
            next_span = span.find_next_siblings('span')
            property_json['Lot_size'] = next_span[0].text.strip()
            break

    for span in soup.findAll('span'):
        if span.text.strip() == 'Year built:':
            next_span = span.find_next_siblings('span')
            property_json['Year_build'] = next_span[0].text.strip()
            break


    for span in soup.findAll('span'):
        if span.text.strip() == 'Type:':
            next_span = span.find_next_siblings('span')
            property_json['Type'] = next_span[0].text.strip()
            break

    for (i, script) in enumerate(soup.findAll('script',attrs={'type': 'application/ld+json'})):
        try:
            if i == 0:
                json_data = json.loads(script.text)
                property_json['Number of Rooms'] = json_data['numberOfRooms']
                property_json['Floor Size (in sqft)'] = json_data['floorSize']['value']
                property_json['Street'] = json_data['address']['streetAddress']
                property_json['Locality'] = json_data['address']['addressLocality']
                property_json['Region'] = json_data['address']['addressRegion']
                property_json['Postal_Code'] = json_data['address']['postalCode']
            if i == 1:
                json_data = json.loads(script.text)
                property_json['Price in $'] = json_data['offers']['price'] 
                property_json['Image'] = json_data['image'] 
            break
        except:
            break
    return property_json

# print(url)
# property_json, html = get_url_details('https://www.zillow.com/homedetails/305-Deer-Run-Ct-Pennington-NJ-08534/64525656_zpid/')
# print(property_json)
# property_list = url_generator(url)
# with open('/Users/cl3720/Desktop/data.json', 'w') as outfile:
#     json.dump(property_list, outfile, indent=4)

url = 'https://www.zillow.com/pennington-nj/sold/'
_, html = get_home_cards(url)

with open('/Users/cl3720/Desktop/output_file.html', 'wb') as file:
    file.write(html)

print ('———-Extraction of data is complete. Check json file.———-')
