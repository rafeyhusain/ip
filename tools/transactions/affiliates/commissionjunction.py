import requests
import pandas
import json
import xmljson

from xml.etree.ElementTree import fromstring
from datetime import timedelta

from affiliates.abstract_affiliates.affiliate import Affiliate
from common.modules import parse, mapper


class CommissionJunction(Affiliate):

    def __init__(self):
        self.affiliate = 'CJ'
        self.url = 'https://commission-detail.api.cj.com/'
        self.api_version = 'v3'
        self.private_key = '0094268e6c19a4f1a8fd227e66486025bacb2c2e74ac70835c4882720938360a29dcc3b7f13f4d290f5a28d9' \
                           'b3fe5155c6c341b8b31183cdc9653dcd59269a44d5/736ef759d34169ea3a123e5a83da268bbcf2d7dfa0dca' \
                           '9fda5a1be28e0db7a5ea4443f08b71823471666cfd5d33e0df5bbdf8090f9de43b8c8606afdaac4f301'

        self.websites_ids_countries = {
            '7222670': 'MY',
            '7227624': 'SG',
            '7235442': 'ID',
            '7236511': 'VN',
            '7227631': 'PH',
            '7306110': 'TH',
            '7234621': 'HK'
        }

    def get_transactions(self, start_date, end_date):
        data = self.request(start_date, end_date)
        if len(data) > 0:
            country = data.apply(lambda x: self.detect_cc(str(x['cj:website-id']),
                                                          x['cj:advertiser-name']), axis=1)

            data = mapper.map_to_ipg(
                data,
                id=data['cj:commission-id'],
                order_value=data['cj:sale-amount'],
                commision=data['cj:commission-amount'],
                status=data.apply(lambda x: self.detect_status(x['cj:action-status'], x['cj:sale-amount']), axis=1),
                cc=country,
                timestamp=data.apply(lambda x: parse.parse_datetime(x['cj:event-date'], "%Y-%m-%dT%H:%M:%S-%f"),
                                     axis=1),
                advertiser_info=data['cj:aid'],
                order_id=country + data.apply(
                    lambda x: filter(str.isdigit, str(x['cj:order-id'])) or str(x['cj:order-id']), axis=1),
                currency='USD',
                device='',
                ip='',
                user_agent='',
                source=data['cj:sid'],
                affiliate_network=self.affiliate,
                deal_type='CPS',
                exit_url='',
                merchant_name=data['cj:advertiser-name'],
                merchant_id=data.apply(lambda x: self.affiliate + str(x['cj:cid']), axis=1)
            )

            data = self.convert_transactions(data)

        return data

    def request(self, start_date, end_date):
        url = self.url + self.api_version + '/commissions'
        headers = {
            'authorization': self.private_key
        }
        payload = {
            'date-type': 'event',
            'start-date': start_date.strftime('%Y-%m-%d') + 'T00:00:00.000Z',
            'end-date': (end_date + timedelta(days=1)).strftime('%Y-%m-%d') + 'T00:00:00.000Z',
        }

        response = requests.get(url, headers=headers, params=payload, timeout=600)
        response = json.dumps(xmljson.parker.data(fromstring(response.text)))
        response = json.loads(response)
        output = pandas.DataFrame(response['commissions']['commission'])

        if len(output) > 0:
            output = output.rename(columns=lambda x: 'cj:' + x)

        return output

    def detect_cc(self, website_id, advertiser):
        # get cc from website id
        if pandas.notnull(website_id) and website_id in self.websites_ids_countries:
            return self.websites_ids_countries[website_id]

        # if that isn't set either, take the advertiser name
        cc = parse.detect_cc_name(advertiser)
        if pandas.notnull(cc):
            return cc

        return ''

    def detect_status(self, status, value):
        if pandas.notnull(status):
            if value < 0:
                return "rejected"

            if status == "new":
                return "pending"
            elif status == "extended":
                return "pending"
            elif status == "locked":
                return "approved"
            elif status == "closed":
                return "approved"

        return pandas.np.nan

    def convert_transactions(self, data):
        # first sort by orderId (so we can iterate) and orderValue (so that the actual value is first)
        data.sort_values(["ipg:orderId", "ipg:orderValue"], ascending=False, inplace=True)

        order_index = None
        count = 0
        for index, row in data.iterrows():
            if order_index and data.loc[index]['ipg:orderId'] == data.loc[order_index]['ipg:orderId']:
                count = count + 1
                if data.loc[index]['ipg:orderValue'] < 0:
                    # substract amount from first basket
                    data.at[order_index, 'ipg:orderValue'] = data.loc[order_index]['ipg:orderValue'] + data.loc[index][
                        'ipg:orderValue']
                    data.at[order_index, 'ipg:commission'] = data.loc[order_index]['ipg:commission'] + data.loc[index][
                        'ipg:commission']
                    # make these positive values
                    data.at[index, 'ipg:orderValue'] = -1 * data.loc[index]['ipg:orderValue']
                    data.at[index, 'ipg:commission'] = -1 * data.loc[index]['ipg:commission']
            else:
                order_index = index
                count = 0

        return data
