import requests
from bs4 import BeautifulSoup
import product




url = "https://www.microcenter.com/search/search_results.aspx?N=4294966995&rd=1&vkw=cpu"
response = requests.get(url)

# Parse  HTML content
soup = BeautifulSoup(response.text, "lxml")


className = "standardDiscount"
# Extract specific data
# print("finish", soup)
titles = soup.find_all('h1')
discount_list = soup.find_all("div", {"class": className})

product_objs = []


productWrapper = "product_wrapper"
product_list = soup.find_all("li", {"class": productWrapper})
for product in product_list:
    for description in product.find_all("div", {"class": "result_right"}):
        for detail in description.find_all("div", {"class": "details"}):
            for price in detail.find_all("div", {"class": "price_wrapper"}):
                for priceClass in 
                print(price)

# for discount in discount_list:
    # print(discount.text)