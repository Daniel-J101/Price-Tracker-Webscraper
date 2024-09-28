import requests
import json
import os
import pandas as pd
from time import gmtime, strftime
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials, firestore
import uuid
import base64
import firebase_manager
import time

############ Global Variables ############
#set this to True when you want the JSON to be read and written locally
local_testing = False
start_time = time.time()
red_text = "\033[91m"
green_text = "\033[92m"
yellow_text = "\033[93m"
normal_text = "\033[0m"


#helper used to identify products when sent to cloud storage
def create_uuid():
    uid = uuid.uuid4()
    short_uid = base64.urlsafe_b64encode(uid.bytes).rstrip(b'=').decode('utf-8')
    return short_uid

############ Connect to the cloud storage ############
service_account_path = 'secrets/serviceAccountKey.json'
db = None
try:
    creds = credentials.Certificate(service_account_path)
    firebase_admin.initialize_app(creds)
    db = firestore.client()
except:
    print("Failed to connect to the cloud storage. ")


############ Scrape the data from the website ############
url = "https://www.microcenter.com/search/search_results.aspx?Ntk=all&sortby=match&N=4294966995&myStore=false&storeID=155"
response = requests.get(url)

soup = BeautifulSoup(response.text, "html.parser")

scraped_product_list = []
for i in range(3):
    scraped_product_list.append(soup.find("li", {"id": f"pwrapper_{i}"}))


############ Create product objects from scraped data ############
product_obj_list = []
for product in scraped_product_list:
    name = product.find("div", {"class": "h2"}).find("a")['data-name']
    price_data = float(product.find("div", {"class": "h2"}).find("a")['data-price'])
    try:
        stock = product.find("span", {"class": "inventoryCnt"}).text
    except:
        stock = "OUT OF STOCK"
    latest_change = strftime("%Y-%m-%d %H:%M", gmtime())
    link = "https://www.microcenter.com" + product.find("div", {"class": "h2"}).find("a")['href']    
    product_obj_list.append({
        'name': name,
        'prices': [
            {
                'amount': price_data,
                'timestamp': latest_change,
            }
        ],
        'stock': stock,
        'price_change': "N/A",
        'link': link
    })

############ Update the product data in the JSON so it can be fetched from frontend ############
json_file_path = 'outputs/products.json'
if os.path.exists(json_file_path):
    with open(json_file_path, 'r') as file:
        existing_data = json.load(file)
else:
    existing_data = []

# Convert existing data into dictionary w/ product names
existing_products = None
if local_testing:
    existing_products = {product['name']: product for product in existing_data}
else:
    product_list = firebase_manager.get_products_from_firebase(db)
    existing_products = {product['name']: product for product in product_list}

# Iterate over the scraped product data
at_least_one_updated = False
at_least_one_created = False
for product in product_obj_list:
    #extrat data from the object
    name = product['name']
    price_data = product['prices'][0]
    stock = product['stock']
    price_change = product['price_change']
    link = product['link']

    if name in existing_products:
        #the price has changed
        if existing_products[name]['prices'][-1]['amount'] != price_data['amount']:
            at_least_one_updated = True
            print(f"Found updated data for {name}!")
            
            #added to the array of prices
            existing_products[name]['prices'].append(price_data)
            
            #update rest of vars
            existing_products[name]['stock'] = stock
            existing_products[name]['link'] = link
            
            #calculate price change
            previous_price = existing_products[name]['prices'][-2]['amount']
            current_price = price_data['amount']
            change_percentage = round((current_price - previous_price) / previous_price * 100)
            change_case = "+" if current_price - previous_price > 1 else "-"
            
            existing_products[name]['price_change'] = f"{change_case}{change_percentage}%" 
    else:
        at_least_one_created = True
        product['id'] = create_uuid()
        existing_products[name] = product

if not at_least_one_updated:
    print(f"{yellow_text}No new data for existing products was found in the scrape.{normal_text}")
else:
    print(f"{green_text}Updated data for existing products successfully.{normal_text}")
if not at_least_one_created:
    print(f"{yellow_text}No new products were found in the scrape.{normal_text}")
else:
    print(f"{green_text}New products successfully added to the data.{normal_text}")
# Convert the dictionary back to a list
updated_product_list = list(existing_products.values())


############ Use the Updated Data ############
if local_testing:
    # Write the updated data back to a local JSON file
    with open(json_file_path, 'w') as file:
        json.dump(updated_product_list, file, indent=4)
else:
    firebase_manager.send_products_to_firebase(updated_product_list, db)    

print(f"{green_text}Product data uploaded successfully. Cron job took {time.time() - start_time:.2f} seconds to complete.{normal_text}")



# test_new_data = [
#     {
#         "name": "Ryzen 9 7950X3D Raphael AM5 4.2GHz 16-Core Boxed Processor - Heatsink Not Included",
#         "prices": [
#             {
#                 "amount": 649.99,
#                 "timestamp": "2024-09-28 21:24"
#             }
#         ],
#         "stock": "25+ IN STOCK",
#         "price_change": "N/A",
#         "link": "https://www.microcenter.com/product/674513/amd-ryzen-9-7950x3d-raphael-am5-42ghz-16-core-boxed-processor-heatsink-not-included"
#     },
#     {
#         "name": "Ryzen 7 7800X3D Raphael AM5 4.2GHz 8-Core Boxed Processor - Heatsink Not Included",
#         "prices": [
#             {
#                 "amount": 529.99,
#                 "timestamp": "2024-09-28 21:24"
#             }
#         ],
#         "stock": "OUT OF STOCK",
#         "price_change": "N/A",
#         "link": "https://www.microcenter.com/product/674503/amd-ryzen-7-7800x3d-raphael-am5-42ghz-8-core-boxed-processor-heatsink-not-included"
#     },
#     {
#         "name": "Ryzen 7 7700X Raphael AM5 4.5GHz 8-Core Boxed Processor - Heatsink Not Included",
#         "prices": [
#             {
#                 "amount": 329.99,
#                 "timestamp": "2024-09-28 21:24"
#             }
#         ],
#         "stock": "25+ IN STOCK",
#         "price_change": "N/A",
#         "link": "https://www.microcenter.com/product/674502/amd-ryzen-7-7700x-raphael-am5-45ghz-8-core-boxed-processor-heatsink-not-included"
#     }
# ]