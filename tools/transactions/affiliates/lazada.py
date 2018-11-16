from datetime import datetime

from abstract_affiliates.hasoffers import HasOffers


class Lazada(HasOffers):

    def __init__(self):
        HasOffers.__init__(
            self,
            affiliate='lazada',
            network_id='lazada',
            api_key='d7fb242b4dd56d243ccdfc435509fc8e454ebbd0e351801a116e67eec7a1a283',
            merchant_name='lazada',
            merchant_id='LZ',
        )

    def get_transactions(self, start_date, end_date):
        data = HasOffers.get_transactions(self, start_date, end_date)

        if len(data) > 0:
            data['ipg:orderValue'] = data.apply(lambda x: (float(x['ho:Stat.payout']) / 0.0641) if (
                'mobile app' in x['ho:Offer.name'].lower() and
                datetime.strptime(x['ho:Stat.datetime'], '%Y-%m-%d %H:%M:%S') <= datetime(2016, 5, 31)) else
                x['ho:Stat.sale_amount'], axis=1)

        return data
