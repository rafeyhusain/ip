import os
import pandas
import sys
import tempfile
import time
import signal

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from threading import Thread
from common.modules import logger

TIMEOUT = 120
TMP_DIR = tempfile.mkdtemp()
MAX_RUN_TIME = 300
finished = False
LOGGER = logger.get_logger('transactions', 'browser_modules')


def setup_driver():
    profile = FirefoxProfile()
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk",
                           "text/plain,application/csv,application/download,application/octet-stream,text/csv,"
                           "application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.dir", TMP_DIR)

    driver = webdriver.Firefox(firefox_profile=profile)

    thread = Thread(target=kill_driver, args=(driver.service.process.pid,))
    thread.start()

    driver.implicitly_wait(TIMEOUT)

    return driver


def wait_for(condition_function):
    start_time = time.time()
    while time.time() < start_time + TIMEOUT:
        if condition_function():
            return True
        else:
            time.sleep(0.1)
    raise Exception('Timeout waiting for {}'.format(condition_function.__name__))


class wait_for_page_load(object):
    def __init__(self, browser):
        self.browser = browser

    def __enter__(self):
        self.old_page = self.browser.find_element_by_tag_name('html')

    def page_has_loaded(self):
        new_page = self.browser.find_element_by_tag_name('html')
        return new_page.id != self.old_page.id

    def __exit__(self, *_):
        wait_for(self.page_has_loaded)


# link http://selenium-python.readthedocs.io/waits.html
def wait_for_element_load(driver, element_identifier):
    WebDriverWait(driver, TIMEOUT).until(
        EC.presence_of_element_located((By.ID, element_identifier))
    )


def download(filename, cleanup=True, remove_bom=False, num_first_line=0, num_end_line=0):
    absolute = ''
    timeout = TIMEOUT
    while True:
        time.sleep(5)
        timeout -= 5
        for entry in os.listdir(TMP_DIR):
            if filename in entry:
                filename = entry.replace(".part", "")
                if remove_bom:
                    absolute = move_to_no_bom_file(filename, num_first_line, num_end_line)
                else:
                    absolute = os.path.join(TMP_DIR, filename)
                break
        if os.path.isfile(absolute):
            break
        elif timeout <= 0:
            LOGGER.error("Downloading timeout", {'filename': filename})
            break

    if os.path.isfile(absolute):
        if ".xls" in filename:
            df = pandas.read_excel(absolute)
        else:
            df = pandas.read_csv(absolute)
    else:
        df = pandas.DataFrame()

    if cleanup and os.path.isfile(absolute):
        os.remove(absolute)

    return df


def move_to_no_bom_file(filename, num_first_line, num_end_line):
    absolute = os.path.join(TMP_DIR, filename)
    new_file = os.path.join(TMP_DIR, 'no_bom_' + filename)

    old = open(absolute)
    lines = old.readlines()
    old.close()
    new = open(new_file, 'w')
    new.writelines(lines[num_first_line:-num_end_line])
    new.close()

    os.remove(absolute)

    return new_file


def close_driver(driver):
    global finished

    driver.quit()
    finished = True


def kill_driver(pid):
    global finished

    run_time = 0

    while True:
        run_time += 5
        time.sleep(5)

        if finished:
            break

        if not finished and run_time >= MAX_RUN_TIME:
            try:
                os.kill(pid, signal.SIGTERM)
                LOGGER.error('kill_driver', {'pid': pid})
            except OSError as e:
                LOGGER.error(e.message)

            break
