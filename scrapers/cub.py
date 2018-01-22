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

class cub_scraper(object):
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client['products']
        self.db_collection = self.db['cub_products']

        resp = input('Are you sure to delete?')
        if 'y' in resp:
            print('deleting')
            self.db_collection.remove({})
        self.driver = webdriver.Chrome()

        self.zip_code = '55420'
        self.store_name = 'Cub Foods'
        self.duplicate_item_count = 0
        self.run()

    def run(self):
        self.driver.get('https://shop.cub.com/')

        self.login()

        #Produce
        categories = ['Dairy & Eggs', 'Frozen', 'Snacks', 'Pantry',
                      'Beverages', 'Meat & Seafood', 'Canned Goods', 'Bakery',
                      'Dry Goods & Pasta', 'Deli', 'Bulk', 'International', 'Breakfast']

        for self.category in categories:
            category_url = self.get_category(self.category)
            self.sub_categories = self.get_sub_categories(self.category)
            print(self.category, self.sub_categories)
            base_category_url = self.driver.current_url
            if len(self.sub_categories)==0:
                self.get_sub_category(None, base_category_url)
            else:
                for self.sub_category in self.sub_categories:
                    self.get_sub_category(self.sub_category, base_category_url)

    def login(self):
        WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, 'log-in')))
        self.driver.find_element_by_css_selector("a[class='log-in']").click()
        username = self.driver.find_element_by_name('email')
        username.send_keys('nicholas.reichel@gmail.com')
        password = self.driver.find_element_by_name('password')
        password.send_keys('Cubpassword2')
        self.driver.find_element_by_class_name('rcp-form-submit-button').click()
        WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.LINK_TEXT, 'Departments')))
        """
        try:
            WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.ID, 'free-delivery-notification-content')))
            buttons = self.driver.find_elements_by_tag_name('button')
            for button in buttons:
                if 'Got it' in button.text:
                    button.click()
        except Exception as e:
            pass
        """

    def get_category(self, category):
        self.driver.get('https://shop.cub.com/store/browse')

        WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.LINK_TEXT, category)))
        self.driver.find_element_by_link_text(category).click()
        return self.driver.current_url

    def get_sub_categories(self, category):
        sub_categories_list = []
        try:
            WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, 'aisle')))
            sub_categories = self.driver.find_elements_by_class_name('aisle')
            for cat in sub_categories:
                sub_categories_list.append(cat.text)
        except Exception as e:
            print(e)
            print(category, "No sub_categories found")
        if 'Sales' in sub_categories_list:
            sub_categories_list.remove('Sales')
        if 'Coupons' in sub_categories_list:
            sub_categories_list.remove('Coupons')
        return sub_categories_list

    def get_sub_category(self, sub_category, base_category_url):
        if sub_category is not None:
            self.driver.find_element_by_link_text(sub_category).click()

        # load all the products by scrolling down
        num_of_items = 0
        last_num_of_items = -1
        while num_of_items!=last_num_of_items:
            last_num_of_items = num_of_items
            for i in range(25):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                sleep(.3)
                num_of_items = len(self.driver.find_elements_by_class_name('item-card'))
                if num_of_items>last_num_of_items:
                    break
            if num_of_items>30:
                break

        self.get_item_cards()

        self.driver.get(base_category_url)

    def get_item_cards(self):
        item_cards = self.driver.find_elements_by_class_name('item-card')
        print(self.category, self.sub_category, 'Total Products:', len(item_cards))
        for item in item_cards[:20]:
            self.get_item(item, item_cards.index(item))

    def get_item(self, item, item_index):
        item.click()
        try:
            nutrition_facts = []
            item_url = self.driver.current_url
            WebDriverWait(self.driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, 'nutrition-facts')))
            nutrition_facts = self.driver.find_element_by_class_name('nutrition-facts').text.split('\n')[1:]

        except Exception as e:
            pass

        nutrition_facts_dict = self.create_nutrition_dict(nutrition_facts)
        if nutrition_facts_dict:
            price = self.get_price()
            nutrition_facts_dict = self.get_price_per_serving(nutrition_facts_dict, price[1:])

            nutrition_facts_dict = self.get_product_info(item_index, nutrition_facts_dict, item_url, price)

            self.store_item(nutrition_facts_dict)

        close_button = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, 'icModalClose')))
        close_button.find_element_by_tag_name('button').click()
        sleep(.3)

    def get_product_info(self, item_index, nutrition_facts_dict, item_url, price):

        name = self.driver.find_element_by_class_name('item-title').text
        nutrition_facts_dict['Product Name'] = name
        size = None
        try:
            size = self.driver.find_element_by_class_name('item-size-info').text
            nutrition_facts_dict['Product Size'] = size
        except:
            pass

        nutrition_facts_dict['Price'] = price
        nutrition_facts_dict['Category'] = self.category
        nutrition_facts_dict['Sub-Category'] = self.sub_category
        item_number = item_url.split('_')[1]
        nutrition_facts_dict['Item Number'] = item_number
        nutrition_facts_dict['Item Index'] = item_index
        nutrition_facts_dict['_id'] = nutrition_facts_dict['Product Name']+' ~ '+size+' ~ '+item_number
        return nutrition_facts_dict

    def get_price(self):
        sleep(.1)
        item_elem = self.driver.find_element_by_class_name('item-detail-module')
        try:
            price = item_elem.find_element_by_class_name('item-full-price').find_element_by_tag_name('span').text
        except Exception as e:
            pass
        try:

            price = item_elem.find_element_by_class_name('item-price').find_element_by_tag_name('span').text
        except Exception as e:
            print(e)
        price = price.replace(' each', '')
        return price

    def get_price_per_serving(self, nutrition_facts_dict, price):
        try:
            servings_per_container = nutrition_facts_dict['Servings Per Container']
        except:
            return nutrition_facts_dict

        for key in list(nutrition_facts_dict.keys()):
            if 'Calories' != key and ('Percent' in key or 'mg' in nutrition_facts_dict[key] or 'g' not in nutrition_facts_dict[key]):
                continue
            if key == 'Serving Size':
                continue
            try:
                if 'Calories' != key:
                    total_amount_of_nutrient = float(nutrition_facts_dict[key][:-1])*float(servings_per_container)
                else:
                    total_amount_of_nutrient = float(nutrition_facts_dict[key])*float(servings_per_container)
                if total_amount_of_nutrient != 0:
                    price_per_gram = float(price)/total_amount_of_nutrient
                    nutrition_facts_dict[key+' PPU'] = str(price_per_gram)[:5]
            except Exception as e:
                print(price)
                print(nutrition_facts_dict)
                print(e)
                with open('err.html', 'w') as f:
                    f.write(str(self.driver.page_source.encode()))
                input()
        return nutrition_facts_dict

    def store_item(self, nutrition_facts_dict):
        try:
            post_id = self.db_collection.insert_one(nutrition_facts_dict)
        except Exception as e:
            print('dupicate id', nutrition_facts_dict['Item Number'])

    def create_nutrition_dict(self, nutrition_facts):
        nutrition_facts_dict = {}
        while nutrition_facts:
            this_fact = nutrition_facts.pop(0)
            if '2,000' in this_fact:
                continue

            cut_off = re.search(r'[0-9.]+',this_fact)
            if cut_off is None:
                continue
            else:
                cut_off = cut_off.span()[0]

            key = this_fact[:cut_off].strip()
            if 'about' in key.lower():
                key = key[:-6]
            value = this_fact[cut_off:]
            nutrition_facts_dict[key] = value
            if 'Daily Value' in nutrition_facts[0]:
                nutrition_facts.pop(0)
            if len(nutrition_facts) and '%' in nutrition_facts[0]:
                key = key+' Percent'
                value = nutrition_facts.pop(0)
                nutrition_facts_dict[key] = value

        return nutrition_facts_dict


cub_scraper()
