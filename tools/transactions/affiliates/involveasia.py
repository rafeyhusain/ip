import requests
import pandas
import json

from datetime import date

from affiliates.abstract_affiliates.affiliate import Affiliate
from common.modules import parse, mapper, logger


class InvolveAsia(Affiliate):

    def __init__(self):
        self.affiliate = 'involveasia'
        self.url = 'https://api.involve.asia/api/'
        self.api_key = 'general'
        self.api_secret = 'ieusMm3Im0CKsa6tvpkpu890E4L+f1dKIeLj9hETn7Y='
        self.logger = logger.get_logger('transactions', self.affiliate)

    def get_transactions(self, start_date, end_date):
        # return empty result set before Nov 30th 2017 as ShopStylers is used
        if start_date <= date(2017, 11, 30):
            return pandas.DataFrame()

        data = self.request(start_date, end_date)

        if len(data) > 0:
            data = mapper.map_to_ipg(
                data,
                id=data['ia:conversion_id'],
                order_value=data['ia:sale_amount'],
                commision=data['ia:payout'],
                status=data['ia:conversion_status'],
                cc=data.apply(lambda x: self.detect_cc(x['ia:offer_name']), axis=1),
                timestamp=data.apply(lambda x: parse.parse_datetime(x['ia:datetime_conversion'],
                                                                    "%Y-%m-%d %H:%M:%S"), axis=1),
                advertiser_info=data['ia:offer_name'],
                order_id='',
                currency=data['ia:currency'],
                device='',
                ip='',
                user_agent='',
                source=data['ia:aff_sub1'],
                affiliate_network=self.affiliate,
                deal_type='CPS',
                exit_url='',
                merchant_name=data['ia:offer_name'],
                merchant_id=''
            )

        return data

    def request(self, start_date, end_date):
        token = self.authenticate()
        page = 1
        json_data = []

        while True:
            response = self.request_page(start_date, end_date, page, token)

            json_data.extend(response['data']['data'])

            if response['data']['nextPage'] is None:
                break
            else:
                page += 1

        output = pandas.DataFrame(json_data)

        if len(output) > 0:
            output = output.rename(columns=lambda x: 'ia:' + x)

        return output

    def authenticate(self):
        url = self.url + 'authenticate'

        payload = [('key', self.api_key), ('secret', self.api_secret)]

        headers = {
            'Authorization': 'No Auth'
        }

        response = requests.post(url=url, data=payload, headers=headers, timeout=600)
        data = response.json()

        if response.status_code == 200:
            return data['data']['token']
        else:
            self.logger.error("Authentication error!", {"response": data})

        return None

    def request_page(self, start_date, end_date, page, token):
        url = self.url + 'conversions/range'

        payload = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "page": page
        }

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token
        }

        response = requests.post(url=url, data=json.dumps(payload), headers=headers, timeout=600)
        data = response.json()

        if response.status_code != 200:
            self.logger.error("Request Error!", {"response": data})

        return data

    def detect_cc(self, refer):
        if pandas.notnull(refer):
            country_codes = {
                '(hk)': 'HK',
                '(id)': 'ID',
                '(sg)': 'SG',
                '(th)': 'TH',
                '(vn)': 'VN',
                '(my)': 'MY',
                '(ph)': 'PH'
            }

            refer = refer.lower()

            for cc in country_codes.keys():
                if cc in refer:
                    return country_codes[cc]

        return ''
