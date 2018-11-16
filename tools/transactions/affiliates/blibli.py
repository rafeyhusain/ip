from abstract_affiliates.hasoffers import HasOffers


class BliBli(HasOffers):

    def __init__(self):
        HasOffers.__init__(
            self,
            affiliate='BliBli',
            network_id='affiliateblibli',
            api_key='eb57397bac4b0f307efdc90a1f5c42541f06dd8990da2908a566810164c6bb07',
            merchant_name='BliBli',
            merchant_id='blibli.com',
            currency='IDR'
        )
