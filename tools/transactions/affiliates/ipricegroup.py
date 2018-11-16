import pandas

from abstract_affiliates.hasoffers import HasOffers
from common.modules import parse


class IpriceGroup(HasOffers):

    def __init__(self):
        HasOffers.__init__(
            self,
            affiliate='ipricegroup',
            network_id='ipricegroup',
            api_key='NETJAz6IdhEXRABSEyWJgo2GLHz5mT',
            use_network_api=True
        )

        self.test_orders = {
            'ho:Stat.source': ['test', 'testoffer',
                               'testoffer??utm_medium=referral&utm_source=iprice&utm_campaign=affiliate'],
            'ho:Offer.name': ['iprice test offer', 'MY myVoucher', 'MK1 Offer', 'Test Store', 'Test Company Shop HK',
                              'voucher',
                              'Test Offer'],
            'ho:Stat.affiliate_info1': ['testoffer', 'test', 'Hussein', 'testofferthang'],
            'ho:Stat.affiliate_info2': ['Reza'],
            'ho:Stat.status_code': [21]
        }

    def get_transactions(self, start_date, end_date):
        conversions = HasOffers.get_transactions(self, start_date, end_date)

        if len(conversions) > 0:
            # remove invalid rows from wrong sync
            conversions = conversions[conversions['ho:Stat.pixel_refer'] != 'invalid_conversion']

            # setting order id
            conversions['ipg:orderId'] = conversions.apply(
                lambda x: x['ipg:orderId'] if pandas.notnull(x['ipg:orderId']) and (
                        len(x['ipg:orderId'].strip()) != 0 and str(x['ipg:orderId']).strip() not in ['ORDER_ID',
                                                                                                     'undefined'])
                else pandas.np.nan, axis=1)

            # setting the affiliate to the original one before syncing
            conversions['ipg:sourceAffiliate'] = conversions['ipg:affiliateNetwork']
            conversions['ipg:affiliateNetwork'] = conversions.apply(
                lambda x: parse.detect_original_affiliate(x['ipg:source'],
                                                          x['ho:Stat.affiliate_info4'],
                                                          x['ho:Stat.affiliate_info5']) or x['ipg:affiliateNetwork'], axis=1)

            conversions = self.detect_test_orders(conversions)
            conversions = self.detect_duplicated_orders(conversions)

        return conversions

    def get_performance(self, start_date, end_date):
        performance = HasOffers.get_performance(self, start_date, end_date)

        if len(performance) > 0:
            performance = self.detect_test_orders(performance)
            performance['ipg:sourceAffiliate'] = performance['ipg:affiliateNetwork']

        return performance

    def detect_test_orders(self, data):
        for index, row in data.iterrows():
            for field, values in self.test_orders.iteritems():
                if field in data.columns:
                    if row[field] in values:
                        data.at[index, 'ipg:suspicious'] = "test order"
        return data

    def detect_duplicated_orders(self, data):
        orders_ids = []

        for index, row in data.iterrows():
            if pandas.isnull(row['ipg:orderId']) or \
                    pandas.isnull(row['ipg:orderValue']) or \
                    pandas.isnull(row['ipg:commission']) or \
                    row['ipg:affiliateNetwork'] != 'ipricegroup':
                continue

            order_unique_id = str(row['ipg:orderId']) + str(row['ipg:orderValue']) + str(row['ipg:commission'])
            if order_unique_id in orders_ids:
                data.at[index, 'ipg:suspicious'] = "duplicated order"
            else:
                orders_ids.append(order_unique_id)

        return data

    def get_existing_conversions(self, start_date, end_date):
        conversions = dict()
        params = dict()
        page = 1
        while True:
            params['NetworkId'] = self.network_id
            params['NetworkToken'] = self.api_key
            params['Target'] = 'Report'
            params['Method'] = 'getConversions'
            params['limit'] = 50000
            params['page'] = page
            params['totals'] = 0
            params['filters[Stat.date][conditional]'] = 'BETWEEN'
            params['filters[Stat.date][values][]'] = [start_date.isoformat(), end_date.isoformat()]
            params['fields[]'] = [
                'Stat.id',
                'Stat.affiliate_info4',
                'Stat.pixel_refer',
                'Stat.currency',
                'Stat.source',
                'Stat.ip',
                'Stat.payout',
                'Stat.refer',
                'Stat.revenue',
                'Stat.sale_amount',
                'Stat.session_datetime',
                'Stat.session_ip',
                'Stat.status',
                'Stat.user_agent',
            ]

            r = self.send_request(params)
            for row in r['response']['data']['data']:
                unique_id = str(row['Stat']['affiliate_info4'])
                if unique_id.startswith('id:') and row['Stat']['pixel_refer'] != 'invalid_conversion':
                    conversions[unique_id] = row['Stat']

            if int(r['response']['data']['page']) < int(r['response']['data']['pageCount']):
                page += 1
            else:
                break

        return conversions

    def is_updated_conversion(self, existing_conversion, fields):
        fields = fields.copy()
        currency = existing_conversion['currency']
        fields['payout@' + currency] = "%.5f" % float(fields.pop('payout'))
        fields['revenue@' + currency] = "%.5f" % float(fields.pop('revenue'))
        fields['sale_amount@' + currency] = "%.5f" % float(fields.pop('sale_amount'))

        for key in fields:
            if fields[key] != existing_conversion[key]:
                return True

        return False

    def upsert_conversion(self, fields, conversion_id=None):
        params = dict()
        params['NetworkId'] = self.network_id
        params['NetworkToken'] = self.api_key
        params['Target'] = 'Conversion'

        if conversion_id is None:
            params['Method'] = 'create'
        else:
            params['Method'] = 'update'
            params['id'] = conversion_id

        for key, value in fields.items():
            params['data[%s]' % key] = value

        r = self.send_request(params)

        return r
