import requests
from bs4 import BeautifulSoup

class Product:
    name=""
    price=""
    stock=""


url = "https://www.microcenter.com/search/search_results.aspx?Ntk=all&sortby=match&N=4294966995&myStore=false&storeID=155"
response = requests.get(url)

# Parse  HTML content
soup = BeautifulSoup(response.text, "lxml")


className = "standardDiscount"
# Extract specific data
# print("finish", soup)
titles = soup.find_all('h1')


product_list = []
for i in range(3):
    product_list.append(soup.find("li", {"id": f"pwrapper_{i}"}))

# print(product_list[0].find("div", {"class": "pDescription compressedNormal2"}).find("a")['data-name'])


product_obj_list = []


for product in product_list:
    product_obj = Product()
    product_obj.name = product.find("div", {"class": "pDescription compressedNormal2"}).find("a")['data-name']
    print(product_obj.name)
    product_obj.price = product.find("div", {"class": "pDescription compressedNormal2"}).find("a")['data-price']
    product_obj.stock = product.find("span", {"class": "msgInStock"}).text
    try:
        product_obj.stock = product.find("span", {"class": "msgInStock"}).text
    except:
        product_obj.stock = "OUT OF STOCK"

    product_obj_list.append(product_obj)

