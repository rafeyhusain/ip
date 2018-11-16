# http://dev.commissionfactory.com/V1/Affiliate/Functions/GetTransactions/

import requests
import pandas

from affiliates.abstract_affiliates.affiliate import Affiliate
from common.modules import parse, mapper


class CommissionFactory(Affiliate):

    def __init__(self):
        self.affiliate = 'commissionfactory'
        self.url = 'https://api.commissionfactory.com/'
        self.api_version = 'V1'
        self.api_key = '1870fce31e6d4d7e866630e6c1e6198a'

    def get_transactions(self, start_date, end_date):
        data = self.request(start_date, end_date)

        if len(data) > 0:
            data = mapper.map_to_ipg(
                data,
                id=data['cf:Id'],
                order_value=data['cf:SaleValue'],
                commision=data['cf:Commission'],
                status=data.apply(lambda x: self.detect_status(x['cf:Status']), axis=1),
                cc=data.apply(lambda x: self.detect_cc(x['cf:TrafficSource']), axis=1),
                timestamp=data.apply(
                    lambda x: parse.parse_datetime(self.detect_date_time(x['cf:DateCreated'].split('.')[0]),
                                                   "%Y-%m-%dT%H:%M:%S"), axis=1),
                advertiser_info='',
                order_id=data['cf:OrderId'],
                currency='AUD',
                device='',
                ip=data['cf:CustomerIpAddress'],
                user_agent='',
                source=data['cf:UniqueId'],
                affiliate_network=self.affiliate,
                deal_type='CPS',
                exit_url=data['cf:TrafficSource'],
                merchant_name=data['cf:MerchantName'],
                merchant_id=data['cf:MerchantId']
            )

        return data

    def request(self, start_date, end_date):
        url = self.url + self.api_version + \
              '/Affiliate/Transactions?apiKey=' + self.api_key + \
              '&fromDate=' + start_date.isoformat() + \
              '&toDate=' + end_date.isoformat()

        response = requests.get(url, timeout=600).json()
        output = pandas.DataFrame(response)

        if len(output) > 0:
            output = output.rename(columns=lambda x: 'cf:' + x)

        return output

    def detect_cc(self, traffic_source):
        cc = parse.detect_cc_refer(traffic_source)
        if pandas.notnull(cc):
            return cc

        return ''

    def detect_date_time(self, datetime):
        if type(datetime) is unicode:
            return datetime.decode('utf8')

        return ''

    def detect_status(self, status):
        status_mapping = {
            "Approved": "approved",
            "Pending": "pending",
            "Void": "rejected",
        }

        if pandas.notnull(status):
            return status_mapping[status]

        return ''
