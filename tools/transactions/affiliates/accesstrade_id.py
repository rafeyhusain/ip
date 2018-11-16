from affiliates.abstract_affiliates.affiliate import Affiliate


class AccessTradeID(Affiliate):

    def __init__(self):
        self.affiliate = 'ATID'
        self.url = 'http://www.accesstrade.co.id/'
        self.username = 'sandeep.raj@ipricegroup.com'
        self.password = 'ipricegroup2016'
        self.site_code = '5232'

    def get_transactions(self, start_date, end_date):
        return []
