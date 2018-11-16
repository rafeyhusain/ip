from abstract_affiliates.hasoffers import HasOffers


class BerryBenka(HasOffers):

    def __init__(self):
        HasOffers.__init__(
            self,
            affiliate='berrybenka',
            network_id='berrybenka',
            api_key='6fad99df15d13d45f3bdcec18e08c5a6ae85e7c6e8b46f191d8c8e69e116abae',
            merchant_name='BerryBenka',
            merchant_id='berrybenka.com',
            currency='IDR'
        )
