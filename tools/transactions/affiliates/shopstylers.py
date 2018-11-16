import pandas
from datetime import date

from abstract_affiliates.hasoffers import HasOffers


class ShopStylers(HasOffers):

    def __init__(self):
        HasOffers.__init__(
            self,
            affiliate='shopstylers',
            network_id='sscpa',
            api_key='fd48513d3b1502e9e77d8ec0fd7ba28f43225ea44525d74271bb7706d588e851',
        )

    def get_transactions(self, start_date, end_date):
        # return empty resultset after Nov 30th 2017 as involveasia will be used
        if start_date > date(2017, 11, 30):
            return pandas.DataFrame()

        data = HasOffers.get_transactions(self, start_date, end_date)

        return data
