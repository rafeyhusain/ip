import pandas

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

from affiliates.abstract_affiliates.affiliate import Affiliate
from common.modules import parse, browser, mapper


class AccessTradeTH(Affiliate):

    def __init__(self):
        self.affiliate = 'ATTH'
        self.url = 'https://member.accesstrade.in.th'
        self.username = 'kavitha.daniel@ipricegroup.com'
        self.password = 'ipricegroup2016'
        self.site_code = '4869'

    def get_transactions(self, start_date, end_date):
        data = self.request(start_date, end_date)

        if len(data) > 0:
            data = mapper.map_to_ipg(
                data,
                id=data['at:seqNo'],
                order_value=data['at:Total Price'],
                commision=data['at:Reward Amount'],
                status=data.apply(lambda x: self.parse_status(x['at:Status']), axis=1),
                cc='TH',
                timestamp=data.apply(lambda x: parse.parse_datetime(x['at:Occur Date'], "%Y/%m/%d %H:%M:%S"), axis=1),
                advertiser_info=data['at:Campaign Name'],
                order_id=data['at:Creative Id'],
                currency='THB',
                device='',
                ip='',
                user_agent=data['at:click_user_agent'] if 'at:click_user_agent' in data.columns else '',
                source=data['at:subid'] if 'at:subid' in data.columns else '',
                affiliate_network=self.affiliate,
                deal_type='CPS',
                exit_url='',
                merchant_name=data['at:Campaign Name'],
                merchant_id=''
            )

        return data

    def request(self, start_date, end_date):
        driver = browser.setup_driver()
        try:
            # login
            driver.get(self.url)
            with browser.wait_for_page_load(driver):
                login_user = driver.find_element_by_id('login-username')
                login_user.send_keys(self.username)
                login_pass = driver.find_element_by_id('login-password')
                login_pass.send_keys(self.password, Keys.RETURN)

            # go to report
            driver.get(self.url + '/p/report-result')

            # select date
            date = driver.find_element_by_id('datePeriod')
            date.clear()
            date.send_keys(start_date.strftime('%B %Y'))

            # select site
            sites = Select(driver.find_element_by_id('siteNo'))
            sites.select_by_value(self.site_code)

            # wait for campaigns being loaded
            driver.find_element_by_css_selector('#listCampaign > option')

            # search
            with browser.wait_for_page_load(driver):
                btn = driver.find_element_by_name('btnSearch')
                btn.click()

            browser.wait_for_element_load(driver, 'ToolTables_tblView_3')

            # download
            driver.execute_script("document.getElementById('ToolTables_tblView_3').click()")

            filename = 'ExportAdditionalParamemter_%s_%s.xls' % (self.site_code, start_date.strftime('%Y%m'))
            df = browser.download(filename)
            df = df.rename(columns=lambda x: 'at:' + x)
        finally:
            browser.close_driver(driver)

        return df

    def parse_status(self, status):
        if pandas.notnull(status):
            status = status.lower()

            if status == "approved":
                return "approved"
            elif status == "reject":
                return "rejected"
            elif status == "pending":
                return "pending"

        return pandas.np.nan
