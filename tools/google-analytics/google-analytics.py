#!/usr/bin/python

# TODO:
# - Support for more than 10 metrics, by running multiple queries

import argparse, ConfigParser, datetime, urllib, socket, re, pandas, sys, itertools

from datetime import date, datetime, timedelta
from pprint import pprint

from googleapiclient import sample_tools

reload(sys)
sys.setdefaultencoding("UTF-8")
socket.setdefaulttimeout(60)

# Google Analytics View IDs
GA_IDS = {
    'SG': {
        'IPRICE': '75448761',
        'TODAYONLINE': '168352681',
    },
    'MY': {
        'IPRICE': '75229758',
    },
    'ID': {
        'IPRICE': '75897118',
        'RAPPLER': '146691305',
    },
    'PH': {
        'IPRICE': '75445974',
        'RAPPLER': '146675449',
    },
    'TH': {
        'IPRICE': '79109064',
        'THAIRATH': '169603426',
    },
    'VN': {
        'IPRICE': '75895336',
    },
    'HK': {
        'IPRICE': '75887160',
    }
}

FILTERABLE_DIMENSIONS = {
    'ga:deviceCategory': ['mobile', 'desktop', 'tablet'],
    'ga:medium': ['direct', 'organic', 'referral']
}

argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('cc', type=str, help=('Country code).'))
argparser.add_argument('week', type=(lambda x: x.split("-")[0] + "-" + str(int(x.split("-")[1])).zfill(2)),
                       help=('Week number).'))
argparser.add_argument('query', type=str, help=('Path to query file).'))

PAGE_SIZE = 10000


def call(service, cc, website, week, query):
    start_index = 1
    data = []
    while True:
        page = service.data().ga().get(
            ids='ga:' + GA_IDS[cc][website],
            start_index=start_index,
            max_results=PAGE_SIZE,
            samplingLevel="HIGHER_PRECISION",
            include_empty_rows=False,
            start_date=get_date(week)[0],
            end_date=get_date(week)[1],
            dimensions=query['dimensions'],
            metrics=query['metrics'],
            filters=query['filters'] if query['filters'] else None).execute()

        if 'rows' in page:
            data += page['rows']

        if start_index + PAGE_SIZE <= page['totalResults']:
            start_index = start_index + PAGE_SIZE
        else:
            break
    # if there is a filter add its value to each row
    for key in FILTERABLE_DIMENSIONS.keys():
        if key in query['filters']:
            value = re.findall(key + '==(\w*)', query['filters'])
            for item in data:
                item.extend(value)
    return data


def aggregate_filter_header(header, query):
    # add filtername to the header
    for k in FILTERABLE_DIMENSIONS.keys():
        if query['filters'].find(k) != -1:
            if k in header:
                header.remove(k)
            header.append(k)
    return header


def get_date(week):
    year, week = week.split("-")
    year = int(year)
    week = int(week)

    d = date(year, 1, 1)
    if (d.weekday() <= 3):
        d = d - timedelta(d.weekday())
    else:
        d = d + timedelta(7 - d.weekday())
    dlt = timedelta(days=(week - 1) * 7)
    return (d + dlt).isoformat(), (d + dlt + timedelta(days=6)).isoformat()


def parse_week(value):
    d = datetime.strptime(value, '%Y%m%d')
    year = str(d.isocalendar()[0])
    week = str(d.isocalendar()[1]).zfill(2)
    return week


def parse_month(value):
    d = datetime.strptime(value, '%Y%m%d')
    return datetime.strftime(d, '%m')


def parse_year(value):
    d = datetime.strptime(value, '%Y%m%d')
    return datetime.strftime(d, '%Y')


def parse_date(value):
    d = datetime.strptime(value, '%Y%m%d')
    return datetime.strftime(d, '%Y-%m-%d')


def parse_device(value):
    # most of our affiliate networks don't support tablet, bucket it into mobile
    value = value.lower()
    if value == 'tablet':
        return 'mobile'
    else:
        return value


def split_product_sub(value):
    # for merged format of product and subproduct after week 2016-32
    if value.find('-') != -1:
        product = value[0:value.find('-')]
        sub_product = value[value.find('-') + 1:]
    else:
        product = value
        sub_product = "(not set)"
    if product == 'discovery':
        product = 'shop'
    return [product, sub_product]


def split_dimension(query):
    new_quereies = []
    candidate_filters = []
    listDimensions = query['dimensions'].split(',')
    if len(listDimensions) > 7:
        list_reduced_dimensions = set(listDimensions) - set(FILTERABLE_DIMENSIONS.keys())
        if len(list_reduced_dimensions) > 7:
            print >> sys.stderr, "Warning: Dimension reduction cannot decrease dimensions. Please add more dimensions to filter list."
        else:
            for k in FILTERABLE_DIMENSIONS.keys():
                if len(listDimensions) > 7:
                    if k in listDimensions:
                        listDimensions.remove(k)
                        candidate_filters.append(k)

            list_filters_params = []
            for filter_dimension_name in candidate_filters:
                filter_strings = []
                for filter_value in FILTERABLE_DIMENSIONS[filter_dimension_name]:
                    filter_strings.append(filter_dimension_name + '==' + filter_value)
                list_filters_params.append(filter_strings)
            for i in itertools.product(*list_filters_params):
                tmp_query = query.copy()
                tmp_query['dimensions'] = ','.join(listDimensions)
                tmp_query['filters'] = tmp_query['filters'] + ';' + ';'.join(i)
                new_quereies.append(tmp_query)
        return new_quereies
    else:
        return [query]


def parse_merchant(value):
    split = str(value).split("|")

    merchantName = "n/a"
    merchantCode = "n/a"

    if len(split) > 0:
        if split[0] != "" and split[0] != "nan":
            merchantName = split[0]
    if len(split) > 1:
        if split[1] != "" and split[1] != "nan":
            merchantCode = split[1]

    return (merchantName, merchantCode)


def parse_product(value1, value2, website):
    value1 = value1.lower()
    value2 = value2.lower()

    product, subproduct = 'n/a', 'n/a'

    # media partners don't fully support content groups right now
    if value1 == '(not set)' and website != 'IPRICE':
        product = 'CooD'

    # backwards compatibility with old usage of ga:ContentGroup1
    elif value1 in ['shop', 'brand', 'mixed', 'category', 'search', 'shingle', 'gender', 'list']:
        product = 'shop'

    elif value1 in ['coupons', 'coupon', 'coupon-store', 'coupon-category']:
        product = 'coupon'

    elif value1 in ['static', 'home', 'info', 'page', 'blog', 'redirect']:
        product = 'static'
    elif value1 in ['pc']:
        product = 'pc'
    if value2 != '(not set)':
        subproduct = value2

    elif value1 in ['brand', 'mixed', 'category', 'search']:
        subproduct = value1

    elif value1 in ['coupon-store', 'coupon-category']:
        subproduct = value1

    elif value1 in ['static', 'home', 'info', 'page', 'blog', 'redirect']:
        subproduct = value1
    # real sub-product can be catched by contentGroup5
    elif value1 == 'pc' and value2 in ['model', 'variant', '(not set)']:
        subproduct = value2

    if product == 'n/a' and value1 != '(not set)' and value1 != '':
        print>> sys.stderr, "Warning: Can't parse product '%s'" % value1
    if subproduct == 'n/a' and value2 != '(not set)' and value2 != '':
        print>> sys.stderr, "Warning: Can't parse subproduct '%s'" % value2

    return (product, subproduct)


def process(cc, website, df, week):
    df['ipg:cc'] = cc;
    df['ipg:website'] = website;

    if 'ga:date' in df:
        df['ipg:date'] = df.apply(lambda x: parse_date(x['ga:date']), axis=1)
        df['ipg:year'] = df.apply(lambda x: parse_year(x['ga:date']), axis=1)
        df['ipg:week'] = df.apply(lambda x: parse_week(x['ga:date']), axis=1)
        df['ipg:month'] = df.apply(lambda x: parse_month(x['ga:date']), axis=1)
        df = df.drop('ga:date', 1)
    if 'ga:deviceCategory' in df:
        df['ipg:device'] = df.apply(lambda x: parse_device(x['ga:deviceCategory']), axis=1)

    if 'ga:landingContentGroup1' in df:
        df['ipg:product'] = df.apply(lambda x: parse_product(split_product_sub(x['ga:landingContentGroup1'])[0], '', website)[0], axis=1)
        df['ipg:subProduct'] = df.apply(lambda x: parse_product(split_product_sub(x['ga:landingContentGroup1'])[0],
                                                                split_product_sub(x['ga:landingContentGroup1'])[1],
                                                                website)[1], axis=1)
    if 'ga:dimension6' in df:
        df['ipg:merchantName'] = df.apply(lambda x: parse_merchant(x['ga:dimension6'])[0], axis=1)
        df['ipg:merchantCode'] = df.apply(lambda x: parse_merchant(x['ga:dimension6'])[1], axis=1)
    if 'ga:dimension3' in df:
        df.rename(columns={'ga:dimension3': 'ipg:category'}, inplace=True)
    if 'ga:dimension6' in df:
        df.rename(columns={'ga:dimension6': 'ipg:storeName'}, inplace=True)
    if 'ga:landingContentGroup1' in df:
        df.rename(columns={'ga:landingContentGroup1': 'ipg:pageType'}, inplace=True)
    if 'ga:landingContentGroup2' in df:
        df.rename(columns={'ga:landingContentGroup2': 'ipg:level0Category'}, inplace=True)
    if 'ga:eventLabel' in df:
        df['ipg:merchantName'] = df.apply(lambda x: parse_merchant(x['ga:eventLabel'])[0], axis=1)

    return df


def parse_query(filename):
    filename = filename + '.ini'
    
    config = ConfigParser.RawConfigParser()
    config.read(filename)

    query = {}
    query['dimensions'] = config.get("query", 'dimensions')
    query['metrics'] = config.get("query", 'metrics')
    query['filters'] = config.get("query", 'filters')

    return query


def initialize_service(argv, id):
    service, flags = sample_tools.init(
        argv, id, 'v3', __doc__, __file__, parents=[argparser],
        scope='https://www.googleapis.com/auth/' + id + '.readonly')
    return service


def main(argv):
    args = argparser.parse_args()

    print >> sys.stderr, '# Start: Google Analytics: %s, %s, %s, %s' % (
    args.cc, args.week, args.query, datetime.now().time().isoformat())

    ga = initialize_service(argv, "analytics")

    query = parse_query(args.query)
    headers = query['dimensions'].split(",") + query['metrics'].split(",")

    output = pandas.DataFrame()
    for website in GA_IDS[args.cc]:
        data = []
        queries = split_dimension(query)
        newHeaders = aggregate_filter_header(headers, queries[0])

        for q in queries:
            data += call(ga, args.cc, website, args.week, q)

        if len(data) == 0:
            print >> sys.stderr, 'Warning: Query did not return any data for website %s' % (website)
            continue

        # need to get all columns in if some where cut previously
        df = pandas.DataFrame(columns=headers)
        dfNew = pandas.DataFrame(data, columns=newHeaders)
        df = pandas.concat([df, dfNew])
        df.dropna(axis=1, inplace=True)
        df = process(args.cc, website, df, args.week)

        output = pandas.concat([output, df])
    output.to_csv(sys.stdout, header=True, index=False, columns=sorted(output.columns.values.tolist()),
                  encoding='utf-8-sig')

    print >> sys.stderr, '# End: Keyword Data: %s, %s, %s, %s' % (
    args.cc, args.week, args.query, datetime.now().time().isoformat())


if __name__ == '__main__':
    main(sys.argv)
