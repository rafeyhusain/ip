from abstract_affiliates.affiliategateway import AffiliateGateway


class AffiliateGatewaySG(AffiliateGateway):

    def __init__(self):
        AffiliateGateway.__init__(
            self,
            affiliate='AGSG',
            url='https://www.tagadmin.sg/ws/AffiliateSOAP.wsdl',
            username='affiliate@ipricegroup.com',
            password='Ipricegroup@2016'
        )
