import datetime
import hashlib
import pandas
import re

from common.modules import parse_constants, logger

LOGGER = logger.get_logger('transactions', 'parser_module')


def parse_datetime(value, format="%Y-%m-%d %H:%M:%S"):
    dt = datetime.datetime.strptime(value, format)
    return (dt - datetime.datetime(1970, 1, 1)).total_seconds()


def get_date_from_timestamp(timestamp):
    dt = datetime.datetime.utcfromtimestamp(timestamp)
    return (
            dt.strftime("%Y-%m-%d"),
            dt.strftime("%m"),
            dt.strftime("%Y"),
            str(dt.isocalendar()[1]).zfill(2),
            dt.strftime("%H:%M:%S")
           )

def parse_sql_datetime(value):
    if pandas.notnull(value):
        d = datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
        return datetime.datetime.strftime(d, '%Y-%m-%d %H:%M:%S')

    return pandas.np.nan

def get_datetime_from_timestamp(timestamp, output_format="%Y-%m-%d %H:%M:%S"):
    return datetime.datetime.utcfromtimestamp(timestamp).strftime(output_format)

def detect_cc_refer(refer):
    if pandas.notnull(refer):
        refer = refer.lower()
        if "iprice.hk" in refer:
            return "HK"
        elif "iprice.co.id" in refer:
            return "ID"
        if "iprice.my" in refer:
            return "MY"
        elif "iprice.ph" in refer:
            return "PH"
        elif "iprice.sg" in refer:
            return "SG"
        elif "ipricethailand.com" in refer:
            return "TH"
        elif "iprice.vn" in refer:
            return "VN"
        elif "says.com" in refer:
            return "MY"
        elif "juiceonline.com" in refer:
            return "MY"
        elif "rappler.com" in refer:
            return "PH"

    return pandas.np.nan


def detect_cc_affid(affid):
    if pandas.notnull(affid):
        affid = affid.lower()
        if affid in ['id', 'hk', 'my', 'ph', 'sg', 'th', 'vn']:
            return affid.upper()

    return pandas.np.nan


def detect_cc_name(value):
    if pandas.notnull(value):
        value = value.lower()
        words = re.compile('[^\w ]+').sub('', value).split(" ")
        for w in words:
            if w in ['id', 'hk', 'my', 'ph', 'sg', 'th', 'vn']:
                return w.upper()

        if 'indonesia' in value:
            return 'ID'
        elif 'hong kong' in value:
            return 'HK'
        elif 'hongkong' in value:
            return 'HK'
        elif 'malaysia' in value:
            return 'MY'
        elif 'philippines' in value:
            return 'PH'
        elif 'singapore' in value:
            return 'SG'
        elif 'thailand' in value:
            return 'TH'
        elif 'vietnam' in value:
            return 'VN'
        elif 'viet nam' in value:
            return 'VN'

    return pandas.np.nan


def detect_site(source, cc):
    if pandas.notnull(source) and not is_new_system_source(source):
        matches = re.search("(MP[0-9]{4})", source)
        if matches:
            if matches.groups(0)[0] in parse_constants.PARTNERS:
                return parse_constants.PARTNERS[matches.groups(0)[0]]
            else:
                LOGGER.warning("Invalid partner ID detected", {"source": source, "partner_id": matches.groups(0)[0]})

    return detect_iprice_site_by_cc(cc)


def detect_iprice_site_by_cc(cc):
    if pandas.isnull(cc):
        return "UNKNOWN"

    cc = cc.lower()
    if cc in ['hk', 'my', 'ph', 'sg', 'vn']:
        return "iprice." + cc
    elif cc in "id":
        return "iprice.co.id"
    elif cc in "th":
        return "ipricethailand.com"


def detect_channel(source):
    if pandas.notnull(source) and not is_new_system_source(source):
        matches = re.search("(organic|adwords|newsletter|news|referral|direct|social)", source)
        if matches:
            value = matches.groups(0)[0]
            if value == "newsletter":
                value = "news"
            return value
    return pandas.np.nan


def detect_product(exit_url, source, site, sub_product):
    if 'iprice' not in site.lower():
        return 'CooD'
    else:
        if pandas.notnull(exit_url) and "iprice" in exit_url:
            if "/r/c/" in exit_url or "/coupons/" in exit_url:
                return "coupon"
            else:
                return "shop"

        if pandas.notnull(sub_product):
            if "discovery" in sub_product \
                    or "brand" in sub_product \
                    or "category" in sub_product \
                    or "gender" in sub_product \
                    or "colour" in sub_product \
                    or "series" in sub_product \
                    or "search" in sub_product:
                return "shop"
            elif "pc" in sub_product:
                return "pc"
            elif "coupon" in sub_product \
                    or "store" in sub_product:
                return "coupon"

    if pandas.notnull(source) and not is_new_system_source(source):
        # media partners are always coupon
        matches = re.search("(MP[0-9]{4})", source)
        if matches:
            return "coupon"

        if source == "newsletter":
            return "news"

        # else check against possible values
        matches = re.search("(shop|coupon|blog|pc)", source)
        if matches:
            return matches.group(0)

    return pandas.np.nan


def detect_log_id(source):
    if pandas.notnull(source):
        if is_new_system_source(source):
            return source[32:41]
        else:
            # special case a bug in the generation of source fields
            source = source.replace("self-redirect-301", "redirect")

            fields = source.split("-", 2)
            if len(fields) == 3:
                id = fields[2]
                if len(id) == 11 or len(id) == 10 or len(id) == 9 or len(id) == 20:
                    return id

    return pandas.np.nan


def detect_merchant(value):
    merchant = str(value).strip()
    if merchant in parse_constants.MERCHANTS:
        return parse_constants.MERCHANTS[merchant].split("|")

    return merchant, pandas.np.nan


def detect_orderid(timestamp, cookie_id):
    # otherwise, ordersare made with the same sessionId within 10 seconds are considered one basket
    timestamp = int(timestamp / 10)
    return generate_id([timestamp, cookie_id])


def generate_id(fields):
    string = "ipg/"
    for f in fields:
        string = string + str(f)
    return hashlib.md5(string).hexdigest()


orders = []


def count_order_id(order_id):
    if order_id in orders:
        return 0
    else:
        orders.append(order_id)
        return 1


def detect_cc_from_currency(currency):
    if currency.upper() in parse_constants.CURRENCY_TO_COUNTRY:
        return parse_constants.CURRENCY_TO_COUNTRY[currency]
    else:
        return pandas.np.nan


def detect_currency_from_cc(country):
    if country.upper() in parse_constants.COUNTRY_TO_CURRENCY:
        return parse_constants.COUNTRY_TO_CURRENCY[country]
    else:
        return pandas.np.nan


def is_new_system_source(source):
    return pandas.notnull(source) and 43 < len(source) < 50 and source.startswith('ig')


def detect_transaction_id(source):
    if pandas.notnull(source) and is_new_system_source(source):
        return source[2:32]
    return pandas.np.nan


def detect_offer_id(source):
    if pandas.notnull(source) and is_new_system_source(source):
        if len(source) == 49:
            return decode_base62(source[41:46])
        else:
            return source[41:]
    return pandas.np.nan


def detect_aff_id(source):
    if pandas.notnull(source) and is_new_system_source(source) and len(source) == 49:
        return decode_base62(source[46:49])
    return '2'  # default affiliate id for ipricegroup


def detect_original_affiliate(source, affiliate_info4, affiliate_info5):
    if is_new_system_source(source) \
            and pandas.notnull(affiliate_info5) \
            and str(affiliate_info5) == 'createdByIprice' \
            and pandas.notnull(affiliate_info4) \
            and str(affiliate_info4).startswith('id:') \
            and not str(affiliate_info4).endswith('testoffer'):

        # ex. id:lazada-1234567 -> lazada
        # ex. id:performance-horizon-1234567 -> performance-horizon
        unique_id = str(affiliate_info4)
        affiliate = re.search('(?<=id:)(.*)(?=-)', unique_id).groups()[0]

        return affiliate

    return None


def decode_base62(string):
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    base = len(alphabet)
    strlen = len(string)
    num = 0
    idx = 0
    for char in string:
        power = (strlen - (idx + 1))
        num += alphabet.index(char) * (base ** power)
        idx += 1

    return num


def fix_broken_log_id(source):
    if pandas.notnull(source):
        if '{transaction_id}' in source:
            source_with_fixed_log_id = source.replace('{transaction_id}', 'tttttttttttttttttttttttttttttt')
            return source_with_fixed_log_id
        elif '%7Btransaction_id%7D' in source:
            source_with_fixed_log_id = source.replace('%7Btransaction_id%7D', 'tttttttttttttttttttttttttttttt')
            return source_with_fixed_log_id
        elif source[32:37] == 'P1003':
            source_with_fixed_log_id = source.replace('P1003', 'xxxxxxxxx')
            return source_with_fixed_log_id

    return source
