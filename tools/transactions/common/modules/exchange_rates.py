# https://oxr.readme.io/
# data is cached because the free version of the API has a limit of 1000 calls/month

import calendar
import datetime
import dateutil.parser
import os
import cPickle
import pandas
import requests
import tempfile

FILENAME = "openexchangerates.obj"
APP_ID = "f235da0c106b4df7ad41e1e80052bd2d"
TMP_DIR = tempfile.gettempdir()
AFFILIATE_PAYMENT_DATE = {'ATTH': 18, 'OMG': 28, 'lazada': 15, 'ipricegroup': 10, 'zalora': 17, 'CJ': 23,
                          'shopstylers': 18, 'AGA': 15, 'AGSG': 15, 'MatahariMall': 15, 'default': 15}


class ExchangeRates():
    exchangeRates = {}

    def __init__(self, offset=0):
        self.__load()

    def __load(self):
        absolute = os.path.join(TMP_DIR, FILENAME)
        if os.path.isfile(absolute):
            file = open(absolute, "rb")
            self.exchangeRates = cPickle.load(file)
            file.close()

    def __save(self):
        fd = open(os.path.join(TMP_DIR, FILENAME), "wb")
        cPickle.dump(self.exchangeRates, fd)
        fd.close()

    def get_exchange_rates(self, date):
        if not date in self.exchangeRates:
            r = requests.get("https://openexchangerates.org/api/historical/%s.json?app_id=%s" % (date, APP_ID), timeout=600)
            self.exchangeRates[date] = r.json()['rates']
            self.exchangeRates[date]['USD'] = 1.0
            self.__save()

        return self.exchangeRates[date]


def get_invoice_date(date, affiliate):
    if affiliate not in AFFILIATE_PAYMENT_DATE.keys():
        affiliate = 'default'
    index_date_s = datetime.datetime(date.year, date.month, AFFILIATE_PAYMENT_DATE[affiliate])
    index_date_e = index_date_s + datetime.timedelta(days=calendar.monthrange(date.year, date.month)[1])
    if index_date_e <= datetime.datetime.now():
        return index_date_e
    else:
        return datetime.datetime.now()


ER = ExchangeRates()


def convert(value, transaction_date, old_currency, new_currency, affiliate):
    try:
        value = float(value)
    except ValueError:
        return pandas.np.nan
    except TypeError:
        return pandas.np.nan

    dateTransaction = dateutil.parser.parse(transaction_date)
    date = get_invoice_date(dateTransaction, affiliate)
    oldRate = ER.get_exchange_rates(date.date().isoformat())[old_currency]
    newRate = ER.get_exchange_rates(date.date().isoformat())[new_currency]

    value = float(value) / oldRate * newRate

    return value
