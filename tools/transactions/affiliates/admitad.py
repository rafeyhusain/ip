# https://developers.admitad.com/en/doc/api_en/methods/statistics/statistics-actions/

import requests
import pandas

from base64 import b64encode
from datetime import datetime

from affiliates.abstract_affiliates.affiliate import Affiliate
from common.modules import parse, mapper, logger


class Admitad(Affiliate):

    def __init__(self):
        self.affiliate = 'admitad'
        self.url = 'https://api.admitad.com/'
        self.client_id = '2877d6947b4195fdb300401a83a96b'
        self.client_secret = '7989ae29e1850a6891a6d22b5e8f7f'
        self.scope = 'statistics'
        self.logger = logger.get_logger('transactions', self.affiliate)

    def get_transactions(self, start_date, end_date):
        data = pandas.DataFrame(data=self.request(start_date, end_date, 'statistics/actions'))
        data = data.rename(columns=lambda x: 'aa:' + x)

        data = mapper.map_to_ipg(
            data,
            id=data['aa:action_id'],
            order_value=data['aa:cart'],
            commision=data['aa:payment'],
            status=data.apply(lambda x: self.detect_status(x['aa:status']), axis=1),
            cc=data.apply(lambda x: self.detect_cc(x['aa:click_user_referer'], x['aa:website_name']), axis=1),
            timestamp=data.apply(lambda x: parse.parse_datetime(x['aa:action_date'], "%Y-%m-%d %H:%M:%S"), axis=1),
            advertiser_info='',
            order_id=data['aa:order_id'],
            currency=data['aa:currency'],
            device='',
            ip=data['aa:click_user_ip'],
            user_agent='',
            source=data['aa:subid'],
            affiliate_network=self.affiliate,
            deal_type='CPS',
            exit_url=data['aa:click_user_referer'],
            merchant_name=data['aa:advcampaign_name'],
            merchant_id=data['aa:advcampaign_id']
        )

        return data

    def request(self, start_date, end_date, api_method):
        data = []

        token = self.get_token()
        if pandas.isnull(token):
            self.logger.error("Could not get token")
            exit()

        limit = 200

        # fix api problem if end date > than today's date
        today = datetime.today().date()
        if end_date > today:
            end_date = today

        params = {
            'date_start': start_date.strftime('%d.%m.%Y'),
            'date_end': end_date.strftime('%d.%m.%Y'),
            'limit': limit,
            'offset': 0,
            'order_by': 'date',
            'action_type': 'sale'
        }

        while True:
            query = "&".join(['%s=%s' % item for item in params.items()])
            url = self.url + api_method + '/?' + query

            headers = {'Authorization': 'Bearer ' + token['access_token']}
            response = requests.get(url=url, headers=headers, timeout=600)

            if response.status_code == 400:
                self.logger.error("Couldn't download affiliate", {"response": response.text})
                exit()

            result = response.json()
            data.extend(result['results'])

            params['offset'] += limit
            if params['offset'] > result['_meta']['count']:
                break

        return data

    def get_token(self, ):
        data = self.client_id + ':' + self.client_secret
        data_b64_encoded = b64encode(data)
        url = self.url + 'token/'
        post_payload = 'grant_type=client_credentials&client_id=' + self.client_id + '&scope=' + self.scope
        headers = {
            'Authorization': 'Basic ' + data_b64_encoded,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.post(url=url, data=post_payload, headers=headers, timeout=600)
        if response.status_code == 200:
            return response.json()

        return pandas.np.nan

    def detect_cc(self, refer, website_name):
        cc = parse.detect_cc_refer(refer)
        if pandas.notnull(cc):
            return cc

        cc = website_name.decode('utf8')[-2:]
        if cc in ['ID', 'HK', 'MY', 'PH', 'SG', 'TH', 'VN']:
            return cc

        return ''

    def detect_status(self, status):
        status_mapping = {
            'pending': 'pending',
            'approved': 'approved',
            'declined': 'rejected',
            'approved_but_stalled': 'pending'
        }

        if pandas.notnull(status):
            return status_mapping[status]

        return pandas.np.nan
