from abstract_affiliates.hasoffers import HasOffers


class Zalora(HasOffers):

    def __init__(self):
        HasOffers.__init__(
            self,
            affiliate='zalora',
            network_id='zalorasea',
            api_key='60f10cb0a51c93ac9d0cd39943896e07dc948d8cfa33900a944c296a82032e7f',
            merchant_name='zalora',
            merchant_id='ZA',
        )
