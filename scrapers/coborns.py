from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from time import sleep
import pprint
from pymongo import MongoClient
import sys
pp = pprint.PrettyPrinter()

class coborns_scraper(object):
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client['products']
        self.db_collection = self.db['coborns_products']
        """
        resp = input('Would you like to update?')
        if 'y' in resp:
            print('deleting')
            self.db_collection.remove({})
        """

        self.driver = webdriver.Chrome()
        self.zip_code = '55420'
        self.store_name = 'Coborns'
        self.run()

    def run(self):
        self.get_main_page()

        categories = self.driver.find_element_by_class_name('bsw-page-head-categories')
        categories = categories.find_elements_by_tag_name('li')

        categories_texts = []
        for i in categories:
            categories_texts.append(i.text)

        excluded_categories = ['Home Entertainment', 'Household Goods', 'Infant & Toddler', 'Personal Care'
                               'Pet Care', 'Store Brands', 'Seasonal & Holiday', 'Beer, Wine, Spirits']
        for category in categories_texts:
            if category in excluded_categories:
                continue
            self.get_category(category)
            self.get_main_page()

    def get_main_page(self):
        self.driver.get('https://www.cobornsdelivers.com/areasolrsearch.action?facilityId=100&catalog=PRODUCTS&areaId=4433&locationCode=NAV_CATALOG')
        categories = self.driver.find_element_by_class_name('bsw-page-head-categories')
        categories.find_elements_by_tag_name('li')[-1:][0].click()

    def get_category(self, category):
        self.category = category
        print('Cat:',category)
        self.driver.find_element_by_link_text(category).click()

        # load all the products by scrolling down
        num_of_items = 0
        last_num_of_items = -1
        while num_of_items!=last_num_of_items:
            last_num_of_items = num_of_items
            for i in range(7):
                frame = self.driver.find_element_by_class_name('bsw-main')
                self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', frame)
                sleep(1)
                num_of_items = len(self.driver.find_elements_by_class_name('bsw-lists-grid-item'))
                if num_of_items>last_num_of_items:
                    break


        item_links = self.get_item_links()
        for self.item_link in item_links:
            self.get_item(self.item_link)

    def get_item_links(self):
        items = []
        items_scraped = self.driver.find_elements_by_class_name('bsw-lists-grid-item')
        for i in items_scraped:
            link = i.find_element_by_tag_name('a').get_attribute('href')
            if self.check_exists(link)==True:
                continue

            product_size = i.find_element_by_class_name('bsw-product-size').text
            product_price_per_unit = i.find_element_by_class_name('bsw-product-price-per-unit').text
            items.append((link, product_size, product_price_per_unit))

        return items
    def check_exists(self, item_link):
        item_num = item_link.split('productId=')[1].split('&')[0]
        result = self.db_collection.find_one({'Product ID': item_num})

        if result is None:
            return False
        else:
            return True


    def get_item(self, item_link):
        self.driver.get(self.item_link[0])
        product_dict = {}
        try:
            self.driver.find_element_by_link_text('Nutrition').click()
            nutrion_facts = self.driver.find_element_by_class_name('bsw-nutrition-facts')
            product_dict = self.get_nutrition_dict(nutrion_facts.text, product_dict)

        except Exception as e:
            pass


        product_dict = self.get_product_info(product_dict)
        pp.pprint(product_dict)

        self.store_item(product_dict)

    def get_nutrition_dict(self, nutrition_facts, nutrition_facts_dict):
        nutrition_facts_list = nutrition_facts.split('\n')

        for fact in nutrition_facts_list:
            try:
                cutoff = re.search(r'[0-9.]+', fact)
                key = fact[:cutoff.span()[0]]
                value = fact[cutoff.span()[0]:cutoff.span()[1]]
                if '*' in key:
                    break
                nutrition_facts_dict[key] = float(value)
            except:
                pass

        return nutrition_facts_dict

    def get_product_info(self, product_dict):
        product_id = self.driver.find_element_by_class_name('bsw-product-id').text.split(': ')[1]
        product_price = self.driver.find_element_by_class_name('bsw-product-price').text.replace(" SALE",'').replace('$','')
        product_name = self.driver.find_element_by_class_name('bsw-product-name').text
        product_dict['Product ID'] = product_id
        product_dict['Product Price'] = product_price
        product_dict['Product Name'] = product_name
        product_dict['_id'] = product_name+' ~ '+product_id
        product_dict['Category'] = self.category
        product_dict['Product Size'] = self.item_link[1]
        product_dict['Product Price Per Unit'] = self.item_link[2]
        return product_dict

    def store_item(self, product_dict):
        try:
            post_id = self.db_collection.insert_one(product_dict)
        except Exception as e:
            print('dupicate id', nutrition_facts_dict['Item Number'])


coborns_scraper()
