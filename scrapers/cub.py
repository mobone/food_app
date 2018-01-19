from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from time import sleep

def login(driver):
    WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, 'log-in')))
    driver.find_element_by_css_selector("a[class='log-in']").click()
    username = driver.find_element_by_name('email')
    username.send_keys('nicholas.reichel@gmail.com')
    password = driver.find_element_by_name('password')
    password.send_keys('Cubpassword2')
    driver.find_element_by_class_name('rcp-form-submit-button').click()
    WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.LINK_TEXT, 'Departments')))

def get_category(driver, category):
    driver.get('https://shop.cub.com/store/browse')
    WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.LINK_TEXT, category)))
    driver.find_element_by_link_text(category).click()
    return driver.current_url

def get_sub_categories(driver, category):
    sub_categories_text = []
    try:
        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, 'aisle')))
        sub_categories = driver.find_elements_by_class_name('aisle')

        for cat in sub_categories:
            sub_categories_text.append(cat.text)
    except:
        print(category, "No sub_categories found")

    return sub_categories_text

def get_item_cards(driver):
    WebDriverWait(driver, 3).until(EC.presence_of_elements_located((By.CLASS_NAME, 'item-card')))
    item_cards = driver.find_elements_by_class_name('item-card')
    print(item_cards)


driver = webdriver.Chrome()
driver.get('https://shop.cub.com/')

login(driver)

categories = ['Produce', 'Dairy & Eggs', 'Frozen', 'Snacks', 'Pantry',
              'Beverages', 'Meat & Seafood', 'Canned Goods', 'Bakery',
              'Dry Goods & Pasta', 'Deli', 'Bulk', 'International', 'Breakfast']
for category in categories:
    category_url = get_category(driver, category)
    sub_categories = get_sub_categories(driver, category)
    print(category, sub_categories)
