#!/usr/bin/python

import argparse
import calendar
import datetime
import sys
import os

import downloader
from common.modules import parse, calculation, logger

reload(sys)
sys.setdefaultencoding("UTF-8")

argparser = argparse.ArgumentParser(add_help=True)
argparser.add_argument('month', type=str, help='Year and month in format: YYYY-MM')
argparser.add_argument('affiliate', type=str, help='Affiliate or all')
argparser.add_argument('type', type=str, help='transactions or performance')

LOGGER = logger.get_logger('transactions', 'download')


def main():
    args = argparser.parse_args()
    LOGGER.info('Process Start', {
        'affiliate': args.affiliate,
        'month': args.month,
        'type': args.type
    })

    # 0. calculate time frame
    (year, month) = map(int, args.month.split("-"))
    start_date = datetime.date(year, month, 1)
    end_date = datetime.date(year, month, calendar.monthrange(year, month)[1])

    # 1. download
    if args.affiliate.upper() == "ALL":
        affiliates = os.listdir(os.path.abspath("affiliates"))
    else:
        affiliates = [args.affiliate + ".py"]

    data = downloader.get_data(affiliates, start_date, end_date, args.type)

    if len(data) > 0:
        # fixing log id for coupons with tracking id (5 chars) instead of log id (9 chars)
        data['ipg:source'] = data.apply(lambda x: parse.fix_broken_log_id(x['ipg:source']), axis=1)

        # filter out only old system transactions
        data['old_system'] = data.apply(
            lambda x: ('ipg:sourceAffiliate' in data.columns and x['ipg:sourceAffiliate'] == 'ipricegroup')
            or not parse.is_new_system_source(x['ipg:source']), axis=1)
        data = data[data['old_system'] == True]

        data = downloader.process_data(data)
        if type == 'transactions':
            LOGGER.info("Calculating basket size data")
            data = calculation.calc_basket_size(data)
        downloader.export_csv(data)

    LOGGER.info('Process Ended: ', {
        'affiliate': args.affiliate,
        'month': args.month,
        'type': args.type
    })


if __name__ == '__main__':
    main()
