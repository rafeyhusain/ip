# coding=utf-8
# !/usr/bin/python

import codecs, pandas, json, re, sys
from collections import OrderedDict
from lxml import html

reload(sys)
sys.setdefaultencoding("UTF-8")


# Simple Counts

def get_links(dom):
    links = []
    elements = dom.cssselect("a[href]")
    for e in elements:
        if ('iprice' in e.get('href') and not "#" in e.get('href')) or (
                not "http" in e.get('href') and not "#" in e.get('href')):
            links.append(e.get('href'))

    return links


def get_field(field, row):
    if field in row['_source']:
        return str(row['_source'][field])
    else:
        return ''


def get_array(field, row):
    if field in row['_source']:
        return row['_source'][field]
    else:
        return ''


def calculate_stats(data):
    stats = []
    for row in data:
        topText = get_field('shortText', row)
        leftText = get_field('sideText', row)
        bottomText = get_field('text', row)

        if not topText and not bottomText and not leftText:
            continue

        domTopText = html.fragment_fromstring(topText, create_parent="div")
        domLeftText = html.fragment_fromstring(leftText, create_parent="div")
        domBottomText = html.fragment_fromstring(bottomText, create_parent="div")

        links = []
        links += get_links(domBottomText)
        links += get_links(domLeftText)
        links += get_links(domTopText)

        for link in links:
            stat = OrderedDict()
            stat['URL'] = "/" + get_field('url', row) + "/"
            stat['CC'] = row['_index'].split("_")[1]
            stat['Type'] = row['_type']
            stat['Link'] = link

            stats.append(stat)

    return stats


def read_data(filename):
    data = []
    with codecs.open(filename, 'r', 'utf-8') as data_file:
        for row in data_file:
            try:
                data.append(json.loads(row))
            except ValueError, e:
                print >> sys.stderr, "WARNING: can't parse row - %s" % row
    return data


def output(stats):
    output = pandas.DataFrame(stats, columns=stats[0].keys())
    output.to_csv(sys.stdout, header=True, index=False, encoding='utf-8-sig')


data = read_data(sys.argv[1])
stats = calculate_stats(data)
output(stats)
