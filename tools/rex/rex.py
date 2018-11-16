#!/usr/bin/python

import codecs, pandas, json, re, sys
from collections import OrderedDict

reload(sys)
sys.setdefaultencoding("UTF-8")


def get_field(field, row):
    if field in row['_source']:
        return str(row['_source'][field])
    else:
        return ''


def get_definition(field, row):
    if 'definitions' in row['_source']:
        for definition in row['_source']['definitions']:
            if definition['field'] == field:
                return definition['value']

    return ""


def count_definitions(row):
    count = 0
    if 'definitions' in row['_source']:
        for definition in row['_source']['definitions']:
            count = count + 1

    return count


def has_condition(field, row):
    if 'conditions' in row['_source']:
        for condition in row['_source']['conditions']:
            if condition['field'] == field:
                return True

    return False


def count_operator(field, row):
    count = 0
    if 'conditions' in row['_source']:
        for condition in row['_source']['conditions']:
            if condition['operator'] == field:
                count = count + 1

    return count


def has_operator(field, row):
    if 'conditions' in row['_source']:
        for condition in row['_source']['conditions']:
            if condition['operator'] == field:
                return True

    return False


def count_field(field, row):
    count = 0
    if 'conditions' in row['_source']:
        for condition in row['_source']['conditions']:
            if condition['field'] == field:
                count = count + 1

    return count


def count_connectors(field, row):
    count = 0
    if 'conditions' in row['_source']:
        for condition in row['_source']['conditions']:
            if condition['connector'] == field:
                count = count + 1

    return count


def get_array(field, row):
    if field in row['_source']:
        return ','.join(row['_source'][field])
    else:
        return ''


def calculate_stats(data):
    stats = []
    for row in data:
        stat = OrderedDict()
        stat['ID'] = row['_id']
        stat['Type'] = row['_type']
        stat['Name'] = get_field('name', row)
        stat['Published'] = get_field('published', row)
        stat['Origin'] = get_field('origin', row)
        stat['Created'] = get_field('created', row)
        stat['Updated'] = get_field('updated', row)
        stat['Parent'] = get_field('parent', row)
        stat['Countries'] = get_array('countries', row)
        stat['IcecatID'] = get_field('specsReference', row)
        stat['Brand'] = get_definition('brand', row)
        stat['Series'] = get_definition('series', row)
        stat['Model'] = get_definition('model', row)
        stat['Category'] = get_definition('category', row)
        stat['C1.Name'] = get_definition('c1-name', row)
        stat['C1.Value'] = get_definition('c1-value', row)
        stat['C2.Name'] = get_definition('c2-name', row)
        stat['C2.Value'] = get_definition('c2-value', row)
        stat['C3.Name'] = get_definition('c3-name', row)
        stat['C3.Value'] = get_definition('c3-value', row)

        stat['D_ALL'] = count_definitions(row)
        stat['O_REGEX'] = has_operator('1.2', row) or has_operator('1.4', row)
        stat['O_CONTAINS'] = count_operator('1.1', row) + count_operator('1.3', row)
        stat['O_MATCHES'] = count_operator('2.1', row) + count_operator('2.2', row)
        stat['O_SMALLER_THAN'] = count_operator('3.1', row)
        stat['O_GREATER_THAN'] = count_operator('3.2', row)
        stat['O_MEDIAN'] = count_operator('4.1', row)
        stat['F_NAME'] = count_field('name', row)
        stat['F_CATEGORY'] = count_field('category', row)
        stat['F_BRAND'] = count_field('brand', row)
        stat['F_MODEL'] = count_field('model', row)
        stat['F_SERIES'] = count_field('series', row)
        stat['F_PRICE'] = count_field('price', row)
        stat['F_COLOR'] = count_field('color', row)
        stat['F_SKU'] = count_field('sku', row)
        stat['F_STORE'] = count_field('store', row)
        stat['F_GENDER'] = count_field('gender', row)
        stat['F_MASTERBRAIN'] = count_field('masterbrain', row)
        stat['C_AND'] = count_connectors('if', row)
        stat['C_OR'] = count_connectors('or', row)

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
