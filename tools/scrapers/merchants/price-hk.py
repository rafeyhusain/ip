# coding=utf-8
# python price-hk.py -o price-hk.csv


# no scrapy because http://www.price.com.hk/starshop_list.php throws httperror 403
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains

import re, os, sys

reload(sys)
sys.setdefaultencoding("utf-8")

chromedriver = "C:/analyze shingles/chromedriver_win32/chromedriver.exe"
os.environ["webdriver.chrome.driver"] = chromedriver
browser = webdriver.Chrome(chromedriver)

browser.get('http://www.price.com.hk/starshop_list.php')  # website with list of merchants
links = []
for merchant in browser.find_elements_by_css_selector("#star-groups ul > li"):  # collect links to merchants page
    url = merchant.find_element_by_css_selector("a[href^='starshop.php']")
    links.append(url.get_attribute("href"))
for link in links:  # open merchants page and collect information
    browser.get(link)
    name = browser.find_elements_by_css_selector(".breadcrumb-product div")[-1]
    merchant = name.get_attribute("innerText")
    try:
        count = browser.find_element_by_css_selector(".pagination-total > span")
        products = re.sub("[^0-9]", "", count.get_attribute("innerText"))
    except Exception, e:
        products = 0
    print link.split("/")[3], merchant, products
browser.quit()
