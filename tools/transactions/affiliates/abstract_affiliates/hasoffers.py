import pandas
import requests
import time
import traceback
from datetime import timedelta

from abc import ABCMeta, abstractmethod

from affiliates.abstract_affiliates.affiliate import Affiliate
from common.modules import parse, parse_constants, mapper, logger


class HasOffers(Affiliate):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(
            self,
            affiliate,
            network_id,
            api_key,
            merchant_name=None,
            merchant_id=None,
            currency=None,
            use_network_api=False
    ):
        self.affiliate = affiliate
        self.url = 'https://api.hasoffers.com/Apiv3/json'
        self.network_id = network_id
        self.api_key = api_key
        self.merchant_name = merchant_name
        self.merchant_id = merchant_id
        self.currency = currency
        self.use_network_api = use_network_api
        self.logger = logger.get_logger('transactions', affiliate)

    def get_transactions(self, start_date, end_date):
        params = dict()
        params['Method'] = 'getConversions'
        params['fields[]'] = [
            'Stat.advertiser_info',  # ad_sub1 query parameter
            'Stat.datetime',
            'Stat.refer',  # referrer URL
            'Stat.sale_amount',
            'Stat.ad_id',  # transaction ID for the cookie
            'Stat.id',  # unique ID for the conversion
            'Stat.status',
            'Stat.ip',
            'Stat.user_agent',
            'Stat.affiliate_info4',
            'Stat.affiliate_info5',
            'ConversionsMobile.device_os',
            'Stat.pixel_refer',
        ]

        data = self.request(params, start_date, end_date)

        return self.parse_cps(data)

    def get_performance(self, start_date, end_date):
        params = dict()
        params['Method'] = 'getStats'

        params['groups[]'] = [
            'Stat.date',
            'Offer.name',
            'Stat.source'
        ]
        params['fields[]'] = [
            'Stat.date'
        ]
        params['filters[Stat.payout_type][conditional]'] = 'EQUAL_TO'
        params['filters[Stat.payout_type][values]'] = 'cpc'
        params['filters[Stat.payout][conditional]'] = 'GREATER_THAN'
        params['filters[Stat.payout][values]'] = 0

        data = pandas.DataFrame()

        single_day = start_date
        while single_day <= end_date:
            result = self.request(params, single_day, single_day)
            data = data.append(result, ignore_index=True)
            single_day += timedelta(days=1)

        return self.parse_cpc(data)

    def request(self, params, start_date, end_date):
        output = pandas.DataFrame()

        page = 1
        while True:
            if self.use_network_api:
                params['NetworkToken'] = self.api_key
                params['Target'] = 'Report'
            else:
                params['api_key'] = self.api_key
                params['Target'] = 'Affiliate_Report'

            params['NetworkId'] = self.network_id
            params['limit'] = 50000
            params['page'] = page
            params['totals'] = 0
            params['filters[Stat.date][conditional]'] = 'BETWEEN'
            params['filters[Stat.date][values][]'] = [start_date.isoformat(), end_date.isoformat()]
            params['fields[]'] += [
                'Browser.display_name',
                'Country.name',
                'Offer.name',
                'Stat.affiliate_info1',  # aff_sub1 query parameter
                'Stat.payout',
                'Stat.source',
            ]

            if not self.currency:
                params['fields[]'] += [
                    'Stat.currency'
                ]

            r = self.send_request(params=params)

            data = []
            for row in r['response']['data']['data']:
                entry = dict()
                # parse basic fields
                for field in params['fields[]']:
                    parts = field.split(".")
                    entry['ho:' + field] = row[parts[0]][parts[1]]

                # parse currencies
                if not self.currency:
                    for field in r['response']['data']['currency_columns']:
                        parts = field.split(".")
                        if parts[1] in row[parts[0]]:
                            value = row[parts[0]][parts[1]]
                            field = field.split("@")[0]
                            entry['ho:' + field] = value
                else:
                    entry['ho:Stat.currency'] = self.currency

                data.append(entry)

            if len(data) > 0:
                output = output.append(data, ignore_index=True)
            else:
                break

            if int(r['response']['data']['page']) < int(r['response']['data']['pageCount']):
                page += 1
            else:
                break

        return output

    def send_request(self, params=None):
        while True:
            try:
                r = requests.get(self.url, params=params, timeout=600).json()
                break
            except ValueError as e:
                if 'API usage exceeded rate limit' in e.message:
                    self.logger.warning("Retrying for API limit", {"endpoint": self.url})
                    time.sleep(10)
                    continue
                else:
                    self.logger.error("Request failed", {
                        'endpoint': self.url,
                        'traceback': traceback.format_exc()
                    })
                    raise e
            except Exception as e:
                self.logger.error("Request failed", {
                    'endpoint': self.url,
                    'traceback': traceback.format_exc()
                })
                raise e

        if r['response']['status'] == -1:
            raise Exception(r)

        return r

    def parse_cps(self, data):
        if len(data) > 0:
            country = data.apply(
                lambda x: self.detect_cc(x['ho:Stat.refer'], x['ho:Offer.name'], x['ho:Country.name'],
                                         x['ho:Stat.affiliate_info1'], x['ho:Stat.currency']), axis=1)

            data = mapper.map_to_ipg(
                data,
                id=data['ho:Stat.id'],
                order_value=data['ho:Stat.sale_amount'],
                commision=data['ho:Stat.payout'],
                status=data['ho:Stat.status'],
                cc=country,
                timestamp=data.apply(lambda x: parse.parse_datetime(x['ho:Stat.datetime']), axis=1),
                advertiser_info=data['ho:Stat.advertiser_info'],
                order_id=data['ho:Stat.advertiser_info'],
                currency=data['ho:Stat.currency'],
                device=data.apply(
                    lambda x: self.detect_device(x['ho:Browser.display_name'], x['ho:ConversionsMobile.device_os'],
                                                 x['ho:Offer.name']), axis=1),
                ip=data['ho:Stat.ip'],
                user_agent=data['ho:Stat.user_agent'],
                source=data['ho:Stat.source'],
                affiliate_network=self.affiliate,
                deal_type='CPS',
                exit_url=data['ho:Stat.refer'],
                merchant_name=data['ho:Offer.name'] if self.merchant_name is None else self.merchant_name,
                merchant_id='' if self.merchant_id is None else self.merchant_id + country
            )

        return data

    def parse_cpc(self, data):
        if len(data) > 0:
            data = mapper.map_to_ipg(
                data,
                id='',
                order_value='',
                commision=data['ho:Stat.payout'],
                status="approved",
                cc=data.apply(
                    lambda x: self.detect_cc("", x['ho:Offer.name'], x['ho:Country.name'], x['ho:Stat.affiliate_info1'],
                                             x['ho:Stat.currency']), axis=1),
                timestamp=data.apply(lambda x: parse.parse_datetime(x['ho:Stat.date'], "%Y-%m-%d"), axis=1),
                advertiser_info='',
                order_id='',
                currency=data['ho:Stat.currency'],
                device=data.apply(
                    lambda x: self.detect_device(x['ho:Browser.display_name'], None, x['ho:Offer.name']), axis=1),
                ip='',
                user_agent='',
                source=data['ho:Stat.source'],
                affiliate_network=self.affiliate,
                deal_type='CPC',
                exit_url='',
                merchant_name=data['ho:Offer.name'],
                merchant_id='',
            )

        return data

    def detect_cc(self, refer, offer, country, affsub2, currency):
        # refer URL is always true
        cc = parse.detect_cc_refer(refer)
        if pandas.notnull(cc):
            return cc

        # otherwise use affsub2
        cc = parse.detect_cc_affid(affsub2)
        if pandas.notnull(cc):
            return cc

        # backwards compatibility, detect from offer name
        cc = parse.detect_cc_name(offer)
        if pandas.notnull(cc):
            return cc

        # if that isn't set either, take the user's country
        cc = parse.detect_cc_name(country)
        if pandas.notnull(cc):
            return cc

        # if the country was missed, use the original currency name
        cc = parse.detect_cc_from_currency(currency)
        if pandas.notnull(cc):
            return cc

        return ''

    def detect_device(self, browser, os, offer):
        if os:
            if os in parse_constants.OS:
                return parse_constants.OS[os]
            else:
                self.logger.warning("Couldn't detect device from os", {'os': os})

        if browser:
            if browser in parse_constants.BROWSERS:
                return parse_constants.BROWSERS[browser]
            else:
                self.logger.warning("Couldn't detect device from browser", {'browser': browser})

        # Lazada: "Mobile app", "App"; Zalora: "App"; ShopStylers: "Mobile" / "Mobile app"
        for word in offer.split(" "):
            if word.lower() in ["app", "mobile"]:
                return "mobile"

        return pandas.np.nan
