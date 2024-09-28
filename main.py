import requests
import json
import pandas as pd
from time import gmtime, strftime
from bs4 import BeautifulSoup

url = "https://www.microcenter.com/search/search_results.aspx?Ntk=all&sortby=match&N=4294966995&myStore=false&storeID=155"
response = requests.get(url)

# Parse  HTML content
soup = BeautifulSoup(response.text, "html.parser")

product_list = []
for i in range(3):
    product_list.append(soup.find("li", {"id": f"pwrapper_{i}"}))

product_obj_list = []

for product in product_list:
    name = product.find("div", {"class": "h2"}).find("a")['data-name']
    price = float(product.find("div", {"class": "h2"}).find("a")['data-price'])
    try:
        stock = product.find("span", {"class": "inventoryCnt"}).text
    except:
        stock = "OUT OF STOCK"
    latest_change = strftime("%Y-%m-%d %H:%M", gmtime())
    link = "https://www.microcenter.com" + product.find("div", {"class": "h2"}).find("a")['href']    
    product_obj_list.append({
        'name': name,
        'price': price,
        'stock': stock,
        'latest_change': latest_change,
        'price_change': "N/A",
        'link': link
    })

def write_to_csv(data, filename):
    df = pd.DataFrame(data)
    df.to_csv(f"./{filename}.csv", index=False)

def compare_data(new_data, filename):
    try:
        df = pd.read_csv(f"./{filename}.csv")
    except:
        print("Historical data does not exist")
        return new_data
    old_data = df.to_dict(orient='records')
    for new_product in new_data:
        for old_product in old_data:
            if old_product["name"] == new_product["name"]:
                if old_product["price"] != new_product["price"]:
                    change_percentage = round((new_product['price'] - old_product['price']) / old_product['price'] * 100)
                    change_case = "+" if new_product['price'] - old_product['price'] > 1 else "-"
                    new_product["price_change"] = f"{change_case}{change_percentage}%" 
                else:
                    new_product["latest_change"] = old_product["latest_change"]
    return new_data

new = [{'name': 'Ryzen 9 7950X3D Raphael AM5 4.2GHz 16-Core Boxed Processor - Heatsink Not Included', 'price': 649.99, 'stock': '25+ IN STOCK', 'latest_change': '2024-09-28 17:21', 'price_change': 'N/A', 'link': 'https://www.microcenter.com/product/674513/amd-ryzen-9-7950x3d-raphael-am5-42ghz-16-core-boxed-processor-heatsink-not-included'}, 
       {'name': 'Ryzen 7 7800X3D Raphael AM5 4.2GHz 8-Core Boxed Processor - Heatsink Not Included', 'price': 529.99, 'stock': 'OUT OF STOCK', 'latest_change': '2024-09-28 17:21', 'price_change': 'N/A', 'link': 'https://www.microcenter.com/product/674503/amd-ryzen-7-7800x3d-raphael-am5-42ghz-8-core-boxed-processor-heatsink-not-included'}, 
       {'name': 'Ryzen 7 7700X Raphael AM5 4.5GHz 8-Core Boxed Processor - Heatsink Not Included', 'price': 329.99, 'stock': '25+ IN STOCK', 'latest_change': '2024-09-28 17:21', 'price_change': 'N/A', 'link': 'https://www.microcenter.com/product/674502/amd-ryzen-7-7700x-raphael-am5-45ghz-8-core-boxed-processor-heatsink-not-included'}]
write_to_csv(product_obj_list, 'data')
compare_data(new, 'data')
write_to_csv(new, 'data')

def save_historical(new_data):
    try:
        with open("./historical.json", 'r') as file:
            existing_data = json.load(file)
    except FileNotFoundError:
        # if the file doesn't exist yet, initialize with an empty list
        existing_data = []
    #  extract timestamp from the first record
    timestamp = new_data[0]["latest_change"]
    new_data = [
        {
            "timestamp": timestamp,
            "data": [
                {
                    "name": item["name"],
                    "price": item["price"]
                }
                for item in new_data
            ]
        }
    ]
    existing_data.extend(new_data)
    with open("./historical.json", 'w') as file:
        json.dump(existing_data, file, indent=2)

save_historical(product_obj_list)