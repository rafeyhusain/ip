# Not implemented yet, they make <15$ per month

from affiliates.abstract_affiliates.affiliate import Affiliate


class LinkShare(Affiliate):

    def __init__(self):
        self.url = 'https://login.linkshare.com/sso/login'
        self.username = 'ipricegroup'
        self.password = 'iprice2016'

    def get_transactions(self, start_date, end_date):
        return []

