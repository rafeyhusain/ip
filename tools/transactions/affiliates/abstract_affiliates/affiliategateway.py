import pandas

from abc import ABCMeta, abstractmethod
from suds.cache import NoCache
from suds.client import Client
from suds.xsd.doctor import Import, ImportDoctor

from affiliates.abstract_affiliates.affiliate import Affiliate
from common.modules import parse, mapper, logger


class AffiliateGateway(Affiliate):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, affiliate, url, username, password):
        self.affiliate = affiliate
        self.url = url
        self.username = username
        self.password = password
        self.logger = logger.get_logger('transactions', affiliate)

        self.countries = {
            1637: 'SG',
            2345: 'SG',  # quirk SG
            948: 'SG',  # SG SG
            1638: 'TH',
            1641: 'MY',
            1621: 'MY',  # old MY
            1642: 'ID',
            1624: 'ID',  # quirk ID
            1643: 'VN',
            1644: 'PH',
            1645: 'HK',
        }

    def get_transactions(self, start_date, end_date):
        data = self.request(start_date, end_date)

        if len(data) > 0:
            data = mapper.map_to_ipg(
                data,
                id=data['ag:TransactionId'],
                order_value=data['ag:OrderAmount'],
                commision=data['ag:AffiliateCommissionAmount'],
                status=data.apply(lambda x: self.detect_status(x['ag:ApprovalStatus']), axis=1),
                cc=data.apply(
                    lambda x: self.detect_cc(x['ag:OriginURL'], x['ag:ProgramName'], x['ag:AffiliateSiteId']), axis=1),
                timestamp=data.apply(
                    lambda x: parse.parse_datetime(x['ag:TransactionDateTime'], "%d/%m/%Y %H:%M:%S"), axis=1),
                advertiser_info=data['ag:MerchantName'],
                order_id=data['ag:TransactionId'],
                currency='USD',
                device='',
                ip='',
                user_agent='',
                source=data['ag:AffiliateSubId'],
                affiliate_network=self.affiliate,
                deal_type='CPS',
                exit_url=data['ag:OriginURL'],
                merchant_name=data['ag:MerchantName'],
                merchant_id=data.apply(lambda x: self.affiliate + str(x['ag:MerchantId']), axis=1)
            )

        return data

    def request(self, start_date, end_date):
        imp = Import('http://theaffiliategateway.com/data/schemas')
        client = Client(self.url, doctor=ImportDoctor(imp), cache=NoCache())

        authentication = client.factory.create('AuthenticationType')
        authentication.username = self.username
        authentication.apikey = self.password

        criteria = client.factory.create('CriteriaType')

        criteria.StartDateTime = start_date.isoformat() + ' 00:00:00'
        criteria.EndDateTime = end_date.isoformat() + ' ' + '00:00:00'

        result = client.service.GetSalesData(authentication, criteria)

        data = []
        if result.Transactions:
            for transaction in result.Transactions.Transaction:
                entry = dict()
                for field in transaction:
                    entry[field[0]] = field[1]
                data.append(entry)

        output = pandas.DataFrame()
        if len(data) > 0:
            output = output.append(data, ignore_index=True)
            output = output.rename(columns=lambda x: 'ag:' + x)

        return output

    def detect_cc(self, refer, program, site_id):
        # refer URL is always true
        cc = parse.detect_cc_refer(refer)
        if pandas.notnull(cc):
            return cc

        # use merchant and product
        cc = parse.detect_cc_name(program)
        if pandas.notnull(cc):
            return cc

        # otherwise use site id
        if pandas.notnull(site_id):
            if site_id in self.countries:
                return self.countries[site_id]
            else:
                self.logger.warning("Couldn't detect cc from site id", {"site_id": site_id})

        return ''

    def detect_status(self, status):
        if pandas.notnull(status):
            status = status.lower()

            if status == "approved":
                return "approved"
            elif status == "declined":
                return "rejected"
            elif status == "pending":
                return "pending"

        return pandas.np.nan
