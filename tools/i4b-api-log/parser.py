#!/usr/bin/python

import sys
import re
from datetime import datetime


common_patterns = [
    '(?<=Successfully completed execution)\s\d+(?=\s)',
    '(?<=cc=)[A-Za-z]{2}',
    '(?<=product_id=)\S+(?=})',
    '(?<=Endpoint response body before transformations:\s{"code":)\d+',
    '(?<=Method response body after transformations:\s{"code":\d{3},"message":").+(?=","data)',
    '(?<="availableStoresCount":)\d+'
    ]

request_timeout_patterns = [
    '(?<=Method request body before transformations:\s)\d+',
    '(?<=cc=)[A-Za-z]{2}',
    '(?<=product_id=)\S+(?=})',
    '(?<=Method completed with status:\s)\d+',
    'Execution failed due to a timeout error',
    '(?<="availableStoresCount":)\d+'
]


def parse_by_line(patterns, line):
    """ parsing line base on input patterns"""
    row = []
    for pattern in patterns:
        matched = re.search(pattern, line)
        if matched is not None:
            row.append(matched.group(0))
        else:
            row.append('')
    return row


def execute():
    print "Timestamp,cc,SKU,Status Code,Response Message, Available Stores Count"
    for line in sys.stdin:
        seconds = 0
        row = parse_by_line(common_patterns, line)
        if row[0] == '':
            row = parse_by_line(request_timeout_patterns, line)

        try:
            seconds = float(row[0]) / 1000.0  # will throw value error
        except ValueError as e:
            # log error
            print >> sys.stderr, "error: " + e.message
            print >> sys.stderr, "line: " + line
            continue

        log_item_date_time = datetime.fromtimestamp(seconds).strftime('%Y-%m-%d %H:%M:%S.%f')

        print log_item_date_time + "," + ",".join(row[1:])


if __name__ == '__main__':
    execute()
