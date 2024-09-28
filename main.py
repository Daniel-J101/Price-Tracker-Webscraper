import requests
import json
import os
import pandas as pd
from time import gmtime, strftime
from bs4 import BeautifulSoup


############ Scrape the data from the website ############
url = "https://www.microcenter.com/search/search_results.aspx?Ntk=all&sortby=match&N=4294966995&myStore=false&storeID=155"
response = requests.get(url)

soup = BeautifulSoup(response.text, "html.parser")

scraped_product_list = []
for i in range(3):
    scraped_product_list.append(soup.find("li", {"id": f"pwrapper_{i}"}))

product_obj_list = []


############ Create product objects from scraped data ############
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
json_file_path = 'products.json'
if os.path.exists(json_file_path):
    with open(json_file_path, 'r') as file:
        existing_data = json.load(file)
else:
    existing_data = []

# Convert existing data into dictionary w/ product names
existing_products = {product['name']: product for product in existing_data}

# Iterate over the scraped product data
for product in product_obj_list:
    #extrat data from the object
    name = product['name']
    price_data = product['prices'][0]
    stock = product['stock']
    price_change = product['price_change']
    link = product['link']

    if name in existing_products:
        
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
        existing_products[name] = product

# Convert the dictionary back to a list
updated_product_list = list(existing_products.values())

# Write the updated data back to the JSON file
with open(json_file_path, 'w') as file:
    json.dump(updated_product_list, file, indent=4)

print("JSON file updated successfully.")




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