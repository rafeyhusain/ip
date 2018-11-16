import pandas
import requests
import traceback
from datetime import timedelta

from abc import ABCMeta, abstractmethod

from affiliates.abstract_affiliates.affiliate import Affiliate
from common.modules import parse, mapper, logger


class PerformanceHorizon(Affiliate):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, affiliate, url, merchant_name, merchant_id):
        self.affiliate = affiliate
        self.url = url
        self.merchant_name = merchant_name
        self.merchant_id = merchant_id
        self.limit = 300
        self.logger = logger.get_logger('transactions', affiliate)

    def get_transactions(self, start_date, end_date):
        data = self.request(start_date, end_date)

        if len(data) > 0:
            data = mapper.map_to_ipg(
                data,
                id=data['ph:conversion_item_id'],
                order_value=data['ph:item_value'],
                commision=data['ph:item_publisher_commission'],
                status=data['ph:item_status'],
                cc=data.apply(
                    lambda x: x['ph:country'] if x['ph:country'] in ['ID', 'HK', 'MY', 'PH', 'SG', 'TH', 'VN'] else '',
                    axis=1),
                timestamp=data.apply(lambda x: parse.parse_datetime(x['ph:conversion_time'], "%Y-%m-%d %H:%M:%S"),
                                     axis=1),
                advertiser_info=data['ph:advertiser_reference'],
                order_id=data['ph:conversion_id'],
                currency=data['ph:currency'],
                device=data.apply(lambda x: self.parse_device(x['ph:ref_device']), axis=1),
                ip=data['ph:referer_ip'],
                user_agent=data['ph:ref_device'],
                source=data['ph:publisher_reference'],
                affiliate_network=self.affiliate,
                deal_type='CPS',
                exit_url='', #TODO: use source_referer
                merchant_name=self.merchant_name,
                merchant_id=data.apply(lambda x: self.merchant_id + x['ph:country'], axis=1)
            )

        return data

    def request(self, start_date, end_date):
        end_date = end_date + timedelta(days=1)
        output = pandas.DataFrame()
        url_with_parameters = self.url + '?\
            start_date=' + start_date.isoformat() + '+00%3A00%3A00\
            &end_date=' + end_date.isoformat() + '+00%3A00%3A00\
            &limit=' + str(self.limit)
        offset = 0
        while True:
            url = url_with_parameters + '&offset=' + str(offset)
            while True:
                try:
                    r = requests.get(url, timeout=600).json()
                    break
                except Exception as e:
                    self.logger.error("Request failed!", {
                        "self.url": url,
                        "traceback": traceback.format_exc()
                    })

                    raise e

            data = []
            for row in r['conversions']:
                for purchase in row['conversion_data']['conversion_items']:
                    entry = dict()
                    for row_field in row['conversion_data']:
                        entry[row_field] = row['conversion_data'][row_field]

                    for field in purchase:
                        entry[field] = purchase[field]

                    data.append(entry)

            if len(data) > 0:
                output = output.append(data, ignore_index=True)
                offset += self.limit
            else:
                break
        output = output.rename(columns=lambda x: 'ph:' + x)
        return output

    def parse_device(self, device):
        device = device.lower()
        if device == 'mobile':
            return 'mobile'
        elif device == 'tablet':
            return 'mobile'
        elif device == 'desktop':
            return 'desktop'
        else:
            return pandas.np.nan
