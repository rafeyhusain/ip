from abstract_affiliates.affiliategateway import AffiliateGateway


class AffiliateGatewayAsia(AffiliateGateway):

    def __init__(self):
        AffiliateGateway.__init__(
            self,
            affiliate='AGA',
            url='https://www.tagadmin.asia/ws/AffiliateSOAP.wsdl',
            username='affiliate@ipricegroup.com',
            password='Ipricegroup@2016'
        )
