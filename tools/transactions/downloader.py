import pandas
import sys
import traceback
import importlib
import inspect

from threading import Thread

from affiliates.abstract_affiliates.affiliate import Affiliate
from common.modules import parse, suspicious, log, exchange_rates, logger

MAX_DOWNLOAD_TIMES = 3
LOGGER = logger.get_logger('transactions', 'downloader')


def get_data(affiliates, start_date, end_date, process):
    data = pandas.DataFrame()
    threads = []
    t_buffer = []

    for f in affiliates:
        if f == "__init__.py" or not f.endswith('.py'):
            continue

        module = importlib.import_module("affiliates.%s" % f.split(".")[0])
        cls = get_affiliate_class(module)
        affiliate = cls()
        t = Thread(target=collect_data,
                   args=(download_data, (affiliate, f.split(".")[0], start_date, end_date, process), t_buffer))
        threads.append(t)
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    for r in t_buffer:
        data = data.append(r, ignore_index=True)

    return data


def get_affiliate_class(module):
    classes = [getattr(module, x) for x in dir(module)]
    for cls in classes:
        if inspect.isclass(cls) and Affiliate in inspect.getmro(cls)[1:] and not inspect.isabstract(cls):
            return cls
    return None


def download_data(affiliate, affiliate_name, start_date, end_date, process):
    counter = MAX_DOWNLOAD_TIMES
    data = []
    LOGGER.info("Downloading Affiliate", {
        'affiliate_name': affiliate_name,
        'process': process
    })
    while counter > 0:
        try:
            if process == 'transactions':
                data = affiliate.get_transactions(start_date, end_date)
            if process == 'performance':
                data = affiliate.get_performance(start_date, end_date)
            break
        except Exception:
            if counter > 1:
                LOGGER.warning("Couldn't download affiliate", {
                    'aff_name': affiliate_name,
                    'retries_count': str(abs(counter - 3) + 1),
                    'traceback': traceback.format_exc()
                })
            else:
                LOGGER.error("Couldn't download affiliate", {
                    'aff_name': affiliate_name,
                    'traceback': traceback.format_exc()
                })
            counter -= 1
    LOGGER.info(
        "Finished Downloading",
        {
            'affiliate_name': affiliate_name,
            'process': process
        }
    )

    return data


def collect_data(func, args, t_buffer):
    temp = func(*args)
    if len(temp) > 0:
        t_buffer.append(temp)


def process_data(data):
    # 0. set meta data for script vs manual download
    LOGGER.info("Processing data...")
    data['ipg:download'] = "SCRIPT"

    # 1. detect transaction_id from source
    data['ipg:cookieId'] = data.apply(lambda x: parse.detect_transaction_id(x['ipg:source']), axis=1)

    # 2. dates and times
    df_time = data.apply(lambda x: pandas.Series(parse.get_date_from_timestamp(x['ipg:timestamp'])), axis=1)
    df_time.columns = ['ipg:date', 'ipg:month', 'ipg:year', 'ipg:week', 'ipg:time']
    data = pandas.concat([data, df_time], axis=1)

    # 3. merchant name and id
    data['ipg:merchantId'] = data.apply(
        lambda x: parse.detect_merchant(x['ipg:merchantName'])[1]
        if pandas.isnull(x['ipg:merchantId']) or str(x['ipg:merchantId']).strip() == ''
        else x['ipg:merchantId'], axis=1)
    data['ipg:merchantName'] = data.apply(lambda x: parse.detect_merchant(x['ipg:merchantName'])[0] if str(
        x['ipg:merchantName']).strip() in parse.parse_constants.MERCHANTS.keys() else x['ipg:merchantName'], axis=1)

    # 4. currency conversions
    data['ipg:orderId'] = data.apply(
        lambda x: parse.detect_orderid(x['ipg:timestamp'], x['ipg:cookieId']) if pandas.isnull(
            x['ipg:orderId']) or x['ipg:orderId'] == '' else x['ipg:orderId'], axis=1)
    data['ipg:order'] = data.apply(
        lambda x: parse.count_order_id(x['ipg:orderId']) if x['ipg:dealType'] == 'CPS' else pandas.np.nan, axis=1)
    data['ipg:originalOrderValue'] = data['ipg:orderValue']
    data['ipg:originalCommission'] = data['ipg:commission']
    data['ipg:originalCurrency'] = data['ipg:currency']
    data['ipg:orderValue'] = data.apply(
        lambda x: exchange_rates.convert(x['ipg:orderValue'], x['ipg:date'], x['ipg:currency'], "USD",
                                         x['ipg:affiliateNetwork']),
        axis=1)
    data['ipg:commission'] = data.apply(
        lambda x: exchange_rates.convert(x['ipg:commission'], x['ipg:date'], x['ipg:currency'], "USD",
                                         x['ipg:affiliateNetwork']),
        axis=1)
    data['ipg:currency'] = "USD"
    data['ipg:dealType'] = data.apply(
        lambda x: 'Bonus' if pandas.isnull(x['ipg:orderValue']) and pandas.isnull(x['ipg:source']) and x[
            'ipg:commission'] != 0 else x['ipg:dealType'], axis=1)

    # 5. detect suspicious transactions
    LOGGER.info("Detecting suspicious data")
    data = suspicious.detect(data)

    # 6. detect not set fields from source
    data['ipg:site'] = data.apply(lambda x: parse.detect_site(x['ipg:source'], x['ipg:cc']), axis=1)
    data['ipg:channel'] = data.apply(lambda x: parse.detect_channel(x['ipg:source']), axis=1)

    # 7. enrich information from log database
    data['ipg:logId'] = data.apply(lambda x: parse.detect_log_id(x['ipg:source']), axis=1)
    LOGGER.info("Downloading Log data")
    data = log.get_log_info(data)

    # 8. detect product after log enrich
    data['ipg:product'] = data.apply(
        lambda x: parse.detect_product(x['ipg:exitUrl'], x['ipg:source'], x['ipg:site'], x['ipg:subProduct']), axis=1)

    data['ipg:created'] = data.apply(lambda x: parse.parse_sql_datetime(x['ipg:created']), axis=1)

    return data


def export_csv(data):
    data.drop([column for column in data.columns if not column.startswith("ipg:")], axis=1, inplace=True)
    data.drop(['ipg:advertiserInfo'], axis=1, inplace=True)
    data.to_csv(sys.stdout, columns=sorted(data.columns), index=False, na_rep='nan', encoding='utf-8-sig')
