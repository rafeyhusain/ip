import elasticsearch
import pandas as pd
import urllib3
import warnings
import parse
import logger

from urlparse import urlparse


urllib3.disable_warnings()
warnings.filterwarnings("ignore", ".* using SSL with verify_certs=False is insecure.")

ES = elasticsearch.Elasticsearch(
    ['http://es-master.ipricegroup.com:9200'], verify_certs=False, timeout=30, max_retries=5, retry_on_timeout=True)
LOGGER = logger.get_logger('transactions','log_module')


def get_data(data):
    log_ids = data['ipg:logId'].dropna().unique().tolist()
    log_indexes = "log_hk,log_id,log_my,log_ph,log_sg,log_th,log_vn"
    result = []
    try:
        limit = 10000
        for i in range(0, len(log_ids), limit):
            r = ES.search(index=log_indexes, size=limit, body={"query": {"ids": {"values": log_ids[i:i + limit]}}})
            result += r['hits']['hits']
    except elasticsearch.exceptions.ConnectionError:
        LOGGER.error("Connection Error in Elastic Search!\n", {"index": log_indexes})
    except elasticsearch.exceptions.AuthorizationException:
        LOGGER.error("You do not have access to ES database!\n")
    return result


def process_data(data):
    data_log = []
    for row in data:
        log = dict()
        log['ipg:logId'] = row['_id'] if '_id' in row else pd.np.nan
        log['ipg:sku'] = row['_source']['sku'] \
            if 'sku' in row['_source'] and str(row['_source']['sku']) != '' else pd.np.nan
        log['ipg:created'] = row['_source']['created'] \
            if 'created' in row['_source'] and str(row['_source']['created']) != '' else pd.np.nan
        log['ipg:position'] = row['_source']['position'] \
            if 'position' in row['_source'] and str(row['_source']['position']) != '' else pd.np.nan
        log['ipg:productName'] = row['_source']['name'].replace("'", ' ') \
            if 'name' in row['_source'] and str(row['_source']['name']) != '' else pd.np.nan
        log['ipg:brand'] = row['_source']['brand']['url'] \
            if 'brand' in row['_source'] and str(row['_source']['brand']['url']) != '' else pd.np.nan
        log['tmp:exitUrl'] = urlparse(row['_source']['exitUrl']).path \
            if 'exitUrl' in row['_source'] and row['_source']['exitUrl'] is not None else pd.np.nan
        log['ipg:landingUrl'] = urlparse(row['_source']['landingUrl']).path \
            if 'landingUrl' in row['_source'] and row['_source']['landingUrl'] is not None else pd.np.nan
        log['ipg:category'] = row['_source']['category']['url'].replace("'", ' ') \
            if 'category' in row['_source'] and str(row['_source']['category']['url']) != '' else pd.np.nan
        log['tmp:channel'] = row['_source']['channel'] \
            if 'channel' in row['_source'] and str(row['_source']['channel']).strip() != '' \
            and str(row['_source']['channel']).find('-') == -1 else pd.np.nan
        log['tmp:device'] = row['_source']['device'].replace('tablet', 'mobile') \
            if 'device' in row['_source'] and row['_source']['device'] != '' else pd.np.nan
        log['ipg:subProduct'] = row['_source']['subProduct'] \
            if 'subProduct' in row['_source'] and pd.notnull(row['_source']['subProduct']) else pd.np.nan
        log['tmp:site'] = row['_source']['site'] \
            if 'site' in row['_source'] and str(row['_source']['site']) != '' else pd.np.nan
        log['ipg:userId'] = row['_source']['uuid'] \
            if 'uuid' in row['_source'] and str(row['_source']['uuid']) != '' else pd.np.nan
        log['ipg:campaign'] = row['_source']['campaign'] \
            if 'campaign' in row['_source'] and str(row['_source']['campaign']) != '' else pd.np.nan
        log['ipg:catalogId'] = row['_source']['id'] \
            if 'id' in row['_source'] and str(row['_source']['id']) != '' else pd.np.nan
        log['ipg:couponCode'] = row['_source']['couponCode'] \
            if 'couponCode' in row['_source'] and str(row['_source']['couponCode']) != '' else pd.np.nan
        log['ipg:price'] = row['_source']['price']['sale'] \
            if 'price' in row['_source'] and str(row['_source']['price']['sale']) != '' else pd.np.nan
        log['ipg:discount'] = row['_source']['price']['discount'] \
            if 'price' in row['_source'] and str(row['_source']['price']['discount']) != '' else pd.np.nan
        log['ipg:features'] = row['_source']['features'] \
            if 'features' in row['_source'] and str(row['_source']['features']) != '' else pd.np.nan
        log['tmp:merchantId'] = row['_source']['store']['merchantId'] \
            if 'store' in row['_source'] and 'merchantId' in row['_source']['store'] else pd.np.nan
        log['tmp:merchantName'] = row['_source']['store']['url'] \
            if 'store' in row['_source'] and 'url' in row['_source']['store'] else pd.np.nan
        log['ipg:level0Category'] = row['_source']['level0_category'] \
            if 'level0_category' in row['_source'] else pd.np.nan
        data_log.append(log)

    return pd.DataFrame(data_log).drop_duplicates(subset='ipg:logId', keep='last')


def get_log_info(data):
    raw = get_data(data)

    if len(raw) > 0:
        log_data = process_data(raw)
        results = pd.merge(data, log_data, how='left', on=['ipg:logId'])
        results['ipg:exitUrl'] = results.apply(
            lambda x: x['ipg:exitUrl'] if (pd.isnull(x['tmp:exitUrl'])) else x['tmp:exitUrl'], axis=1)
        results['ipg:device'] = results.apply(
            lambda x: x['tmp:device'] if (str(x['tmp:device']).strip() != '' and pd.notnull(x['tmp:device'])) else x[
                'ipg:device'], axis=1)
        results['ipg:channel'] = results.apply(
            lambda x: x['tmp:channel'] if pd.notnull(x['tmp:channel']) and str(x['tmp:channel']).strip() != '' and str(
                x['tmp:channel']).strip().find('-') == -1 else parse.detect_channel(x['ipg:source']), axis=1)
        results['ipg:site'] = results.apply(
            lambda x: x['tmp:site'] if pd.notnull(x['tmp:site']) and str(x['tmp:site']).strip() != '' else x[
                'ipg:site'], axis=1)
        results['ipg:merchantId'] = results.apply(
            lambda x: x['ipg:merchantId'] if (pd.isnull(x['tmp:merchantId'])) else x['tmp:merchantId'], axis=1)
        results['ipg:merchantName'] = results.apply(
            lambda x: x['ipg:merchantName'] if (pd.isnull(x['tmp:merchantName'])) else x['tmp:merchantName'], axis=1)
        return results
    else:
        data['ipg:sku'] = pd.np.nan
        data['ipg:created'] = pd.np.nan
        data['ipg:position'] = pd.np.nan
        data['ipg:productName'] = pd.np.nan
        data['ipg:brand'] = pd.np.nan
        data['ipg:landingUrl'] = pd.np.nan
        data['ipg:category'] = pd.np.nan
        data['ipg:userId'] = pd.np.nan
        data['ipg:level0Category'] = pd.np.nan
        data['ipg:subProduct'] = pd.np.nan
        data['ipg:campaign'] = pd.np.nan
        data['ipg:catalogId'] = pd.np.nan
        data['ipg:couponCode'] = pd.np.nan
        data['ipg:price'] = pd.np.nan
        data['ipg:discount'] = pd.np.nan
        data['ipg:features'] = pd.np.nan

        return data


def process_sync_data(data):
    data_log = []
    for row in data:
        log = dict()
        log['ipg:logId'] = row['_id'] if '_id' in row else pd.np.nan
        log['ipg:affCustom'] = row['_source']['affCustom'] \
            if 'affCustom' in row['_source'] and pd.notnull(row['_source']['affCustom']) else ''
        data_log.append(log)

    return pd.DataFrame(data_log).drop_duplicates(subset='ipg:logId', keep='last')


def get_sync_log_info(data):
    raw = get_data(data)

    if len(raw) > 0:
        log_data = process_sync_data(raw)
        results = pd.merge(data, log_data, how='left', on=['ipg:logId'])
        return results
    else:
        data['ipg:affCustom'] = ''

        return data
