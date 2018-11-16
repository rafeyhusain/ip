# coding=utf-8
# python websosanh.py > websosanh.csv

# no scrapy because the merchant list disappears when you disable java script

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains

import re, os, sys

reload(sys)
sys.setdefaultencoding("utf-8")

chromedriver = "C:/analyze shingles/chromedriver_win32/chromedriver.exe"
os.environ["webdriver.chrome.driver"] = chromedriver
browser = webdriver.Chrome(chromedriver)

browser.get('https://websosanh.vn/')
links = []  # collect links to merchant websites
for category in browser.find_elements_by_css_selector(".categories .dropdown-menu > li"):
    url = category.find_element_by_css_selector("a[href^='https://websosanh.vn/']")
    links.append(url.get_attribute("href"))
for link in links:  # click on links and collect information
    browser.get(link)
    for merchant in browser.find_elements_by_css_selector("#mCSB_2 label"):
        data = merchant.get_attribute('innerText').split(" ")
        count = re.sub("[^0-9]", "", data[1])
        if count == "":
            count = 0
        else:
            count = int(count)
        print link.split("/")[3], data[0], count
browser.quit()
