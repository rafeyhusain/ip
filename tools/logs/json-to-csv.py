#!/usr/bin/env python
"""
https://iprice.vn/trang-suc/phu-kien/
./node_modules/elasticdump/bin/elasticdump  --bulk=true --limit=50000 --input=http://10.0.254.14:9200/access_logs-14.10.2016_v2 --output=access-logs-14-10-2016.log.json >elasticdump.log 2>&1 &
"""
import json

input_logs = open('access-logs-14-10-2016.log.json').readlines()

hosts = {
    'iprice.hk': open('access-logs-hk.log', 'a+'),
    'iprice.co.id': open('access-logs-id.log', 'a+'),
    'iprice.my': open('access-logs-my.log', 'a+'),
    'iprice.ph': open('access-logs-ph.log', 'a+'),
    'iprice.sg': open('access-logs-sg.log', 'a+'),
    'ipricethailand.com': open('access-logs-th.log', 'a+'),
    'iprice.vn': open('access-logs-vn.log', 'a+')
}

# hosts['iprice.hk'].write('"Date","IP","URL","Parameters","HTTP Code","Size","User Agent"\n')

for log in input_logs:
    json_log = json.loads(log)

    try:
        if json_log['_source']['country'] in [
            'www.coupons.rappler.com',
            'coupon.rappler.com',
            'www.coupon.rappler.com',
            'coupons.rappler.com',
            'coupon.says.com',
            'www.coupon.says.com',
            'www.juiceonline.com',
            'juiceonline.com'
            'www.juiceonline.com'
        ]:
            continue

    except KeyError:
        continue

    buffer = ',,'  # Date, IP
    not_parsed = 0

    try:
        buffer += '"' + json_log['_source']['uri_path'] + '"'
    except KeyError:
        not_parsed += 1
        # print ('Warning: uri_path is missing, skipping')

    buffer += ','

    try:
        buffer += '"' + json_log['_source']['uri_param'] + '"'
    except KeyError:
        not_parsed += 1
        # print ('Warning: uri_path is missing, skipping')

    if not_parsed == 2:
        print ('Line is empty, skipping')
        continue

    buffer += ',,,'  # HTTP Code, Size

    try:
        buffer += json_log['_source']['agent']
    except KeyError:
        print ('Warning: agent is missing, skipping')

    buffer += '\n'

    hosts[json_log['_source']['country']].write(buffer)

for key, handler in hosts.iteritems():
    handler.close()
