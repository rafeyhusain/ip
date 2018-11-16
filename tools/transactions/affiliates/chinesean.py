import pandas

from affiliates.abstract_affiliates.affiliate import Affiliate
from common.captcha import captcha_resolver
from common.modules import parse, browser, mapper


class Chinesean(Affiliate):

    def __init__(self):
        self.affiliate = 'chinesean'
        self.url = 'https://www.chinesean.com'
        self.username = 'iprice'
        self.password = 'ipricegroup2016'

        self.countries_websites = {
            'iPrice': 'MY',
            'iprice singapore': 'SG',
            'iprice indonesia': 'ID',
            'iprice vietnam': 'VN',
            'iprice philippines': 'PH',
            'iprice thailand': 'TH',
            'iprice hong kong': 'HK',
        }

    def get_transactions(self, start_date, end_date):
        data = self.download(start_date, end_date)

        if len(data) > 0:
            data = mapper.map_to_ipg(
                data,
                id=data['cs:Transaction ID'],
                order_value=data['cs:Order Value'],
                commision=data.apply(lambda x: self.detect_commission(x['cs:Commission']), axis=1),
                status=data.apply(lambda x: self.detect_status(x['cs:Status'], x['cs:Order Value']), axis=1),
                cc=data.apply(lambda x: self.detect_cc(x['cs:Website']), axis=1),
                timestamp=data.apply(
                    lambda x: parse.parse_datetime(x['cs:Date (Time)'], "%Y-%m-%d (%H:%M:%S)"), axis=1),
                advertiser_info=data['cs:Program'],
                order_id=data['cs:Creative ID'],
                currency=data.apply(lambda x: self.detect_currency(x['cs:Commission']), axis=1),
                device='',
                ip=data['cs:IP Address'],
                user_agent='',
                source=data['cs:Member Id'],
                affiliate_network=self.affiliate,
                deal_type='CPS',
                exit_url=data['cs:URL'],
                merchant_name=data['cs:Program'],
                merchant_id=data.apply(lambda x: self.affiliate + str(x['cs:Program ID']), axis=1)
            )

        return data

    def download(self, start_date, end_date):
        (year, month, day) = map(str, (str(start_date)).split("-"))
        report_month = "%s-%s" % (year, month)
        screenshot_filename = 'common/captcha/image_chinesean_screenshot.png'
        captcha_filename = 'common/captcha/image_chinesean_captcha.png'
        login_url = self.url + '/affiliate/index.do'

        driver = browser.setup_driver()
        try:
            driver.get(login_url)
            captcha_text = captcha_resolver.get_captcha_text(driver, screenshot_filename, captcha_filename)

            driver.find_element_by_name('username').send_keys(self.username)
            driver.find_element_by_name('password').send_keys(self.password)
            driver.find_element_by_name('verificationCode').send_keys(captcha_text)

            with browser.wait_for_page_load(driver):
                login = driver.find_element_by_tag_name('form')
                login.submit()

            with browser.wait_for_page_load(driver):
                driver.get(self.url + '/affiliate/pb_eventdetails.do')
                driver.execute_script("$('input[type=\"radio\"][name=\"reportPeriodId\"][value=\"1002\"]').click();")
                driver.execute_script("$('select[name=\"reportMonth\"]').val('" + report_month + "');")
                driver.execute_script("$('input[type=\"radio\"][name=\"reportFormatId\"][value=\"1002\"]').click();")
                driver.execute_script("$('input[type=\"image\"]').click();")

            df = browser.download('pbeventdetails', True, True, 2, 2)
            df = df.rename(columns=lambda x: 'cs:' + x)

            browser.close_driver(driver)
        except Exception, e:
            raise e

        return df

    def detect_commission(self, commission):
        if pandas.notnull(commission):
            values = commission.split(" ")
            if len(values) > 1:
                return values[1]

        return ''

    def detect_currency(self, commission):
        if pandas.notnull(commission):
            values = commission.split(" ")
            if len(values) > 1:
                return values[0].replace('RMB', 'CNY')

        return ''

    def detect_cc(self, website):
        if pandas.notnull(website) and website in self.countries_websites:
            return self.countries_websites[website]

        return ''

    def detect_status(self, status, value):
        if pandas.notnull(status):
            status = status.lower()

            if value <= 0:
                return "rejected"
            if status == "pending":
                return "pending"
            if status == "rejected":
                return "rejected"
            elif status == "approved":
                return "approved"

        return ''
