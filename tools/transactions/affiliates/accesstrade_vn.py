import requests
import pandas

from datetime import timedelta

from affiliates.abstract_affiliates.affiliate import Affiliate
from common.modules import parse, parse_constants, mapper, logger


class AccessTradeVN(Affiliate):

    def __init__(self):
        self.affiliate = 'ATVN'
        self.url = 'https://api.accesstrade.vn/'
        self.api_version = 'v1'
        self.access_key = 't4iIdd7-c3TzfaYG7c41SlinVkvjqQWz'
        self.limit = 100
        self.logger = logger.get_logger('transactions', self.affiliate)

    def get_transactions(self, start_date, end_date):
        data = self.request(start_date, end_date)

        if len(data) > 0:
            data = mapper.map_to_ipg(
                data,
                id=data['atv:id'],
                order_value=data['atv:transaction_value'],
                commision=data['atv:commission'],
                status=data.apply(lambda x: self.detect_status(x['atv:status']), axis=1),
                cc='VN',
                timestamp=data.apply(
                    lambda x: parse.parse_datetime(x['atv:transaction_time'], "%Y-%m-%dT%H:%M:%S"), axis=1),
                advertiser_info='',
                order_id=data['atv:transaction_id'],
                currency='VND',
                device=data.apply(lambda x: self.detect_device(x['atv:os'], x['atv:browser']), axis=1),
                ip='',
                user_agent=data.apply(lambda x: x['atv:os'] + ', ' + x['atv:browser'], axis=1),
                source=data['atv:utm_source'],
                affiliate_network=self.affiliate,
                deal_type='CPS',
                exit_url=data['atv:click_url'],
                merchant_name=data['atv:merchant'],
                merchant_id='',
            )

        return data

    def request(self, start_date, end_date):
        start_date = start_date.strftime('%Y-%m-%d') + 'T00:00:00Z'
        end_date = (end_date + timedelta(days=1)).strftime('%Y-%m-%d') + 'T00:00:00Z'
        url_with_parameters = self.url + self.api_version + '/transactions' + \
            '?since=' + start_date + '&until=' + end_date + '&limit=' + str(self.limit)
        headers = {
            'Authorization': 'Token ' + self.access_key,
            'Content-Type': 'application/json',
        }

        data = []
        offset = 0
        while True:
            url = url_with_parameters + '&offset=' + str(offset)

            try:
                response = requests.get(url, headers=headers, timeout=600)

                if response.status_code != 200:
                    raise response.raise_for_status()

                response = response.json()
            except Exception as e:
                raise e

            for row in response['data']:
                for extra in row['_extra']:
                    row[extra] = row['_extra'][extra]
                data.append(row)

            if offset < (response['total'] - self.limit):
                offset += self.limit
            else:
                break

        output = pandas.DataFrame(data)
        output = output.rename(columns=lambda x: 'atv:' + x)

        return output

    def detect_device(self, os, browser):
        if pandas.notnull(os) and os in parse_constants.OS:
            return parse_constants.OS[os]
        else:
            self.logger.warning("Couldn't detect device from os", {'os': os})

        if pandas.notnull(browser) and browser in parse_constants.BROWSERS:
            return parse_constants.BROWSERS[browser]
        else:
            self.logger.warning("Couldn't detect device from browser", {'browser': browser})

        return ''

    def detect_status(self, status):
        status_mapping = {
            0: "pending",
            1: "approved",
            2: "rejected",
        }

        if pandas.notnull(status):
            return status_mapping[status]

        return ''
