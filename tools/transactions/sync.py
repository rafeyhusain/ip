#!/usr/bin/python

import argparse
import calendar
import datetime
import sys
import json
import os

import downloader
from affiliates.ipricegroup import IpriceGroup
from common.modules import parse, log, logger

LOGGER = logger.get_logger('transactions', 'sync')

reload(sys)
sys.setdefaultencoding("UTF-8")

argparser = argparse.ArgumentParser(add_help=True)
argparser.add_argument('month', type=str, help='Year and month')
argparser.add_argument('affiliate', type=str, help='Affiliate or all')
argparser.add_argument('--dry_run', type=str, help='True or False')
argparser.add_argument('--testing', type=str, help='True or False')


def main(argv):
    args = argparser.parse_args()
    LOGGER.info('Sync Process Starts', {
        'month': args.month,
        'affiliate': args.affiliate
    })

    # 0. calculate time frame
    (year, month) = map(int, args.month.split("-"))
    start_date = datetime.date(year, month, 1)
    end_date = datetime.date(year, month, calendar.monthrange(year, month)[1])

    if args.affiliate.upper() == "ALL":
        affiliates = os.listdir(os.path.abspath("affiliates"))
        affiliates.remove('ipricegroup.py')
    else:
        affiliates = [args.affiliate + ".py"]

    dry_run = True if args.dry_run == 'True' else False
    testing = False if args.testing == 'False' else True

    data = downloader.get_data(affiliates, start_date, end_date, 'transactions')

    if len(data) > 0:
        # fixing log id for coupons with tracking id (5 chars) instead of log id (9 chars)
        data['ipg:source'] = data.apply(lambda x: parse.fix_broken_log_id(x['ipg:source']), axis=1)

        # filter out only new system transactions
        data['new_system'] = data.apply(lambda x: parse.is_new_system_source(x['ipg:source']), axis=1)
        data = data[data['new_system'] == True]

    if len(data) > 0:
        # enrich information from log database
        data['ipg:logId'] = data.apply(lambda x: parse.detect_log_id(x['ipg:source']), axis=1)
        LOGGER.info("Downloading Sync Log data")
        data = log.get_sync_log_info(data)

        ipricegroup = IpriceGroup()
        existing_conversions = ipricegroup.get_existing_conversions(start_date, end_date)

        count = {'created': 0, 'updated': 0, 'processed': 0}
        for index, row in data.iterrows():
            count['processed'] += 1
            conversion_unique_id = 'id:' + row['ipg:affiliateNetwork'] + '-' + str(row['ipg:originalConversionId'])
            if testing:
                conversion_unique_id += '-testoffer'
            conversion_datetime = parse.get_datetime_from_timestamp(row['ipg:timestamp'])

            existing_conversion = existing_conversions.get(conversion_unique_id)
            # todo handle the case is sometime calling create/update api continuously doesn't work. HO is not real-time

            affiliate_id = parse.detect_aff_id(row['ipg:source'])
            try:
                if existing_conversion is None:
                    fields = {
                        'ad_id': parse.detect_transaction_id(row['ipg:source']),
                        'advertiser_info': row['ipg:advertiserInfo'],
                        'affiliate_id': affiliate_id,
                        'affiliate_info1': 'testoffer' if testing else row['ipg:cc'],
                        'affiliate_info2': '',
                        'affiliate_info3': row['ipg:affCustom'],
                        'affiliate_info4': conversion_unique_id,
                        'affiliate_info5': 'createdByIprice',
                        'country_code': row['ipg:cc'],
                        'currency': row['ipg:currency'],
                        'datetime': conversion_datetime,
                        'ip': row['ipg:ip'],
                        'is_adjustment': '0',
                        'offer_id': parse.detect_offer_id(row['ipg:source']),
                        'payout': row['ipg:commission'],
                        'refer': row['ipg:exitUrl'],
                        'revenue': row['ipg:commission'],
                        'sale_amount': row['ipg:orderValue'],
                        'session_datetime': conversion_datetime,
                        'session_ip': row['ipg:ip'],
                        'source': row['ipg:source'],
                        'status': row['ipg:status'],
                        'user_agent': row['ipg:userAgent']
                    }

                    LOGGER.info("Create Conversion", {
                        'affiliate_id': affiliate_id,
                        'conversion_id': conversion_unique_id
                    })
                    if dry_run:
                        LOGGER.info("Create dry run fields", fields)
                    else:
                        ipricegroup.upsert_conversion(fields)
                        count['created'] += 1
                    data.loc[index, 'ipg:sync'] = 'created'
                else:
                    fields = {
                        'ip': row['ipg:ip'],
                        'payout': row['ipg:commission'],
                        'refer': row['ipg:exitUrl'],
                        'revenue': row['ipg:commission'],
                        'sale_amount': row['ipg:orderValue'],
                        'session_datetime': conversion_datetime,
                        'session_ip': row['ipg:ip'],
                        'status': row['ipg:status'],
                        'user_agent': row['ipg:userAgent']
                    }

                    if ipricegroup.is_updated_conversion(existing_conversion, fields):
                        LOGGER.info("Update Conversion", {
                            'affiliate_id': affiliate_id,
                            'existing_conversion_id': existing_conversion['id'],
                            'conversion_id': conversion_unique_id
                        })
                        if dry_run:
                            LOGGER.info("Update dry run fields", fields)
                        else:
                            # if we have these fields changed we cannot update the conversion
                            # but we can log it to sync_failed 2 times
                            # 1- the old conversion with negative payout, revenue & sale_Amount
                            # 2- the new conversion with the new values
                            non_updatable_fields = {
                                'currency': 'ipg:currency',
                                'source': 'ipg:source',
                            }
                            for key, field in non_updatable_fields.iteritems():
                                if str(existing_conversion[key]) != str(row[field]):
                                    raise Exception('change of ' + key + ' to ' + str(row[field]) +
                                                    ' are not allowed for an existing conversion: ' +
                                                    json.dumps(existing_conversion))

                            ipricegroup.upsert_conversion(fields, existing_conversion['id'])
                            count['updated'] += 1
                        data.loc[index, 'ipg:sync'] = 'updated'
            except Exception as e:
                data.loc[index, 'ipg:sync'] = 'failed'
                LOGGER.error(str(e), {'affiliate_id': affiliate_id})
        
        LOGGER.info("Processed Conversion", {'count': count['processed']})
        LOGGER.info("Created Conversion", {'count': count['created']})
        LOGGER.info("Updated Conversion", {'count': count['updated']})

        data = downloader.process_data(data)
        downloader.export_csv(data)
    
    LOGGER.info('Sync Process Ended', {
        'month': args.month,
        'affiliate': args.affiliate
    })


if __name__ == '__main__':
    main(sys.argv)
