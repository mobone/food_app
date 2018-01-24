from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from time import sleep
import pprint


class coborns_scraper(object):
    def __init__(self):

        self.driver = webdriver.Chrome()
        self.zip_code = '55420'
        self.store_name = 'Cub Foods'
        self.run()

    def run(self):
        self.get_main_page()
        categories = self.driver.find_element_by_class_name('bsw-page-head-categories')
        categories.find_elements_by_tag_name('li')[-1:][0].click()
        categories = self.driver.find_element_by_class_name('bsw-page-head-categories')
        categories = categories.find_elements_by_tag_name('li')
        categories_texts = []
        for i in categories:
            categories_texts.append(i.text)

        for category in categories_texts:


            self.get_category(category)
            self.get_main_page()


    def get_main_page(self):
        self.driver.get('https://www.cobornsdelivers.com/areasolrsearch.action?facilityId=100&catalog=PRODUCTS&areaId=4433&locationCode=NAV_CATALOG')

    def get_category(self, category):
        print(category)
        self.driver.find_element_by_link_text(category).click()

        # load all the products by scrolling down
        num_of_items = 0
        last_num_of_items = -1
        while num_of_items!=last_num_of_items:
            last_num_of_items = num_of_items
            for i in range(25):
                frame = self.driver.find_element_by_class_name('bsw-main')
                self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', frame)
                sleep(.5)
                num_of_items = len(self.driver.find_elements_by_class_name('bsw-lists-grid-item'))
                if num_of_items>last_num_of_items:
                    break
            if num_of_items>100:
                break

        item_links = self.get_item_links()
        for item_link in item_links:
            self.get_item(item_link)

    def get_item_links(self):
        item_links = []
        items = self.driver.find_elements_by_class_name('bsw-lists-grid-item')
        for i in items:
            item_links.append(i.find_element_by_tag_name('a').get_attribute('href'))

        return item_links

    def get_item(self, item_link):
        self.driver.get(item_link)
        try:
            self.driver.find_element_by_link_text('Nutrition').click()
            nutrion_facts = self.driver.find_element_by_class_name('bsw-nutrition-facts')
            self.get_nutrition_dict(nutrion_facts.text)
        except Exception as e:
            return None

    def get_nutrition_dict(self, nutrition_facts):
        nutrition_facts_list = nutrition_facts.split('\n')
        nutrition_facts_dict = {}
        for fact in nutrition_facts_list:
            try:
                cutoff = re.search(r'[0-9.]+', fact)
                key = fact[:cutoff.span()[0]]
                value = fact[cutoff.span()[0]:cutoff.span()[1]]
                if '*' in key:
                    break
                nutrition_facts_dict[key] = value
            except:
                pass
        print(nutrition_facts_dict)




coborns_scraper()
