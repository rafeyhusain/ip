from abstract_affiliates.hasoffers import HasOffers


class MatahariMall(HasOffers):

    def __init__(self):
        HasOffers.__init__(
            self,
            affiliate='mataharimall',
            network_id='mataharimall',
            api_key='8364d537e84a82afb71e221a076a368d35f49c87ccdedf040e2d2637ee71c948',
            merchant_name='MatahariMall',
            merchant_id='MM101', #TODO change the id to mataharimall.com
            currency='IDR'
        )
