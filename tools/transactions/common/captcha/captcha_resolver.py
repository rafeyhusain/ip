# Imagetyperz captcha API
# ------------------------------

import sys

from imagetypersapi import ImageTypersAPI
from PIL import Image
from common.modules import logger

CAPTCHA_USERNAME = 'admin.ipricegroup.com'
CAPTCHA_PASSWORD = 'Iprice2017!'
LOGGER = logger.get_logger('transactions', 'captcha_resolver')


# solve captcha
def get_captcha_text(driver, screenshot_filename, captcha_filename):
    LOGGER.info("Processing captcha...")

    element = driver.find_element_by_id('vcode')  # get it again here
    size = element.size
    driver.execute_script("document.getElementById('vcode').style.position = 'fixed'")
    driver.execute_script("document.getElementById('vcode').style.left = '0'")
    driver.execute_script("document.getElementById('vcode').style.top = '0'")

    driver.save_screenshot(screenshot_filename)  # saves screenshot of entire page
    image = Image.open(screenshot_filename)  # uses PIL library to open image in memory

    window_size = driver.get_window_size()
    width_ratio = (image.width / float(window_size['width']))
    height_ratio = (image.height / float(window_size['height']))
    ratio = max(width_ratio, height_ratio)

    im = image.crop((0, 0, size['width'] * ratio, size['height'] * ratio))
    im.save(captcha_filename)  # saves new cropped image

    # init captcha api
    username = CAPTCHA_USERNAME
    password = CAPTCHA_PASSWORD
    ita = ImageTypersAPI(username, password)  # init imagetyperz api obj
    captcha_text = ita.solve_captcha(captcha_filename,
                                     case_sensitive=True)  # solve captcha, with case sensitive arg True

    LOGGER.info("Done... captcha text", {'text': captcha_text})
    return captcha_text
