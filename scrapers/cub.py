from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from time import sleep
import pprint

pp = pprint.PrettyPrinter()

class cub_scraper(object):
    def __init__(self):

        self.driver = webdriver.Chrome()
        self.run()
        self.zip_code = '55420'
        self.store_name = 'Cub Foods'
        pass

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
        try:
            WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, 'free-delivery-notification-content')))
            buttons = self.driver.find_elements_by_tag_name('button')
            for button in buttons:
                if 'Got it' in button.text:
                    button.click()
        except Exception as e:
            pass

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
            sub_categories.remove('Sales')
            sub_categories.remove('Coupons')
            for cat in sub_categories:
                sub_categories_list.append(cat.text)
        except:
            print(category, "No sub_categories found")

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



        self.get_item_cards()

        self.driver.get(base_category_url)

    def get_item_cards(self):
        item_cards = self.driver.find_elements_by_class_name('item-card')
        print(self.category, self.sub_category, 'Total Products:', len(item_cards))
        for item in item_cards:
            self.get_item(item)

    def get_item(self, item):
        item.click()
        try:
            nutrition_facts = []
            WebDriverWait(self.driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, 'nutrition-facts')))
            nutrition_facts = self.driver.find_element_by_class_name('nutrition-facts').text.split('\n')[1:]

        except Exception as e:
            print(e)
        self.create_nutrition_dict(nutrition_facts, item.text.split('\n'))

        close_button = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, 'icModalClose')))
        close_button.find_element_by_tag_name('button').click()
        sleep(.3)

    def create_nutrition_dict(self, nutrition_facts, product_info):

        nutrition_facts_dict = {}

        # parse the product info
        nutrition_facts_dict['price'] = product_info.pop(0)
        if '$' in product_info[0]:
            product_info.pop(0) # skip $2.00 off
        nutrition_facts_dict['Product Name'] = product_info.pop(0)
        if product_info:
            nutrition_facts_dict['Product Size'] = product_info.pop(0)
        nutrition_facts_dict['Category'] = self.category
        nutrition_facts_dict['Sub-Category'] = self.sub_category

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
            value = this_fact[cut_off:]
            nutrition_facts_dict[key] = value
            if 'Daily Value' in nutrition_facts[0]:
                nutrition_facts.pop(0)
            if len(nutrition_facts) and '%' in nutrition_facts[0]:
                key = key+' Percent'
                value = nutrition_facts.pop(0)
                nutrition_facts_dict[key] = value
        print('--------')
        pp.pprint(nutrition_facts_dict)





cub_scraper()
