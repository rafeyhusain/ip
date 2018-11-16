#!/usr/bin/python

import codecs
import datetime
import pandas
import json
import sys

from collections import OrderedDict

reload(sys)
sys.setdefaultencoding("UTF-8")



def is_active(timestamp):
    if not timestamp:
        return False

    try:
        expires = datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S')
    except ValueError:
        try:
            expires = datetime.datetime.strptime(timestamp, '%Y-%m-%d')
        except ValueError:
            expires = datetime.datetime.max

    now = datetime.datetime.now()
    if now < expires:
        return True
    else:
        return False


def get_field(field, row):
    if field in row['_source']:
        return row['_source'][field]
    else:
        return ''


def calculate_stats(data):
    stats = []
    for row in data:
        stat = OrderedDict()

        name = get_field('name', row)
        created = get_field('created', row)
        expires = get_field('expires', row)
        label = get_field('label', row)
        referral = get_field('referral', row).lower()
        referral_mobile = get_field('referralMobile', row).lower()
        store = get_field('store', row)['url']
        popularity = get_field('popularity', row)
        ctype = get_field('type', row)

        stat['Name'] = name
        stat['Created'] = created
        stat['Expires'] = expires
        stat['Label'] = label
        stat['Store'] = store
        stat['Popularity'] = popularity
        stat['Active'] = is_active(expires)
        stat['Type'] = ctype
        stat['Referral'] = referral
        stat['ReferralMobile'] = referral_mobile

        stats.append(stat)

    return stats


def read_data(filename):
    data = []
    with codecs.open(filename, 'r', 'utf-8') as data_file:
        for row in data_file:
            data.append(json.loads(row))
    return data


def output(stats):
    output = pandas.DataFrame(stats, columns=stats[0].keys())
    output.to_csv(sys.stdout, header=True, index=False, encoding='utf-8-sig')


data = read_data(sys.argv[1])
stats = calculate_stats(data)
output(stats)
