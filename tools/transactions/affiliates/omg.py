import requests
import pandas
import hashlib

from datetime import datetime, timedelta

from affiliates.abstract_affiliates.affiliate import Affiliate
from common.modules import parse, mapper


class Omg(Affiliate):

    def __init__(self):
        self.affiliate = 'OMG'
        self.url = 'https://api.omgpm.com/network/OMGNetworkApi.svc/'
        self.api_version = 'v1.2.1'
        self.api_key = '03add82e-1448-472f-9223-c52b47f4ea3c'
        self.private_key = '3a1c171c4bdb49448b7795967b7c75b8'
        self.affiliate_id = '521487'

    def get_transactions(self, start_date, end_date):
        data = self.request(start_date, end_date)

        if len(data) > 0:
            data = mapper.map_to_ipg(
                data,
                id=data['omg:TransactionID'],
                order_value=data.apply(
                    lambda x: x['omg:TransactionValue'] if pandas.notnull(x['omg:TransactionValue']) else 0, axis=1),
                commision=data['omg:SR'],
                status=data.apply(lambda x: self.detect_status(x['omg:Status']), axis=1),
                cc=data.apply(
                    lambda x: self.detect_cc(x['omg:Referrer'], x['omg:Merchant'], x['omg:Product'], x['omg:UID2']),
                    axis=1),
                timestamp=data.apply(
                    lambda x: parse.parse_datetime(x['omg:TransactionTime'], '%d/%m/%Y %H:%M:%S'), axis=1),
                advertiser_info=data['omg:Merchant'],
                order_id=data['omg:MerchantRef'],
                currency=data.apply(lambda x: x['omg:Currency'].strip(), axis=1),
                device='',
                ip='',
                user_agent='',
                source=data['omg:UID'],
                affiliate_network=self.affiliate,
                deal_type='CPS',
                exit_url=data['omg:Referrer'],
                merchant_name=data['omg:Merchant'],
                merchant_id=data.apply(lambda x: "OM" + str(x['omg:MID']), axis=1)
            )

        return data

    def request(self, start_date, end_date):
        sig_data = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        sig = hashlib.md5(self.private_key + sig_data).hexdigest()
        url = self.url + self.api_version + '/Reports/Affiliate/TransactionsOverview'

        payload = {
            'Key': self.api_key,
            'Sig': sig,
            'SigData': sig_data,
            'AID': self.affiliate_id,
            'AgencyID': '118',  # Optimise SE Asia, https://kb.optimisemedia.com/?article=agencyids
            'StartDate': start_date,
            'EndDate': end_date,
            'output': 'JSON',
            'Status': -1,
        }

        response = requests.get(url, payload, timeout=600).json()
        output = pandas.DataFrame(response)

        if len(output) > 0:
            # remove conversions not within the date range (api problem)
            transaction_time = pandas.to_datetime(output['TransactionTime'], format='%d/%m/%Y %H:%M:%S')
            start_date = pandas.to_datetime(start_date)
            end_date = pandas.to_datetime(end_date + timedelta(days=1))
            output = output[(transaction_time >= start_date) & (transaction_time < end_date)]

            # remove conversions without transaction id (normally the ones created today)
            output = output[output['TransactionID'] != 0]

            output = output.rename(columns=lambda x: 'omg:' + x)

        return output

    def detect_cc(self, refer, merchant, product, uid2):
        # refer URL is always true
        cc = parse.detect_cc_refer(refer)
        if pandas.notnull(cc):
            return cc

        # use merchant and product
        cc = parse.detect_cc_name(merchant)
        if pandas.notnull(cc):
            return cc

        cc = parse.detect_cc_name(product)
        if pandas.notnull(cc):
            return cc

            # otherwise use uid2
        cc = parse.detect_cc_affid(uid2)
        if pandas.notnull(cc):
            return cc

        return ''

    def detect_status(self, status):
        if pandas.notnull(status):
            status = status.lower()

            if status == "validated":
                return "approved"
            elif status == "rejected":
                return "rejected"
            elif status == "pending":
                return "pending"

        return pandas.np.nan
