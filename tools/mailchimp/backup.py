#!/usr/bin/env python

import sys
import requests
import pandas as pd
import io
import datetime
import os

API_KEY = '152253060783c3b593797f9900eb4afa'
BASE_URL = 'https://us8.api.mailchimp.com/export/1.0/list/'


def process(country, id, output_dir):
    # get response from api
    payload = {'apikey': API_KEY, 'id': id}
    r = requests.get(BASE_URL, params=payload)
    raw_data = pd.read_csv(io.StringIO(r.content.decode('utf-8')))

    # generate csv file from mailchimp api response
    output_path = output_dir + country + '.csv'
    raw_data.to_csv(path_or_buf=output_path)


def main(argv):
    params = argv[1].split(' ')
    process(*params)


if __name__ == '__main__':
    main(sys.argv)
