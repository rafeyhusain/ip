#!/usr/bin/python

import argparse, datetime, socket, sys, urllib3, requests, time, warnings

reload(sys)
sys.setdefaultencoding("UTF-8")
socket.setdefaulttimeout(10)
urllib3.disable_warnings()
warnings.filterwarnings("ignore", ".* using SSL with verify_certs=False is insecure.")

argparser = argparse.ArgumentParser(add_help=False)

CLIENT_ID = "4326"
CLIENT_SECRET = "145rvcD4g1xgxsd6s4s3ss4aCaaF23as"
BASE_URL = "https://platform-api.productsup.io/platform/v1"


def get_sites():
    headers = {'X-Auth-Token': "%s:%s" % (CLIENT_ID, CLIENT_SECRET)}
    r = requests.get("%s/sites" % BASE_URL, headers=headers)
    for site in r.json()['Sites']:
        yield (site['title'], site['id'], site['import_schedule'])


def get_import_history(site):
    headers = {'X-Auth-Token': "%s:%s" % (CLIENT_ID, CLIENT_SECRET)}
    r = requests.get("%s/sites/%s/importhistory" % (BASE_URL, site[1]), headers=headers)

    values = []
    for history in r.json()['Importhistory']:
        values.append((site[0], "import", "", history['import_time'], history['product_count']))
    return values


def get_export_history(site):
    headers = {'X-Auth-Token': "%s:%s" % (CLIENT_ID, CLIENT_SECRET)}
    r = requests.get("%s/sites/%s/channels" % (BASE_URL, site[1]), headers=headers)

    values = []
    for channel in r.json()['Channels']:
        r2 = requests.get("%s/sites/%s/channels/%s/history" % (BASE_URL, site[1], channel['id']), headers=headers)
        for c2 in r2.json()['Channels']:
            for history in c2['history']:
                values.append(
                    (site[0], c2['name'], history['export_start'], history['export_time'], history['product_count']))
    return values


def main(argv):
    args = argparser.parse_args()

    print >> sys.stderr, '# Start: ProductsUp report: %s' % (datetime.datetime.now().time().isoformat())

    print '"%s","%s","%s","%s","%s"' % ("Site", "Name", "Start", "Finish", "Products")
    for site in get_sites():
        for value in get_import_history(site):
            print '"%s","%s","%s","%s","%s"' % (value[0], value[1], value[2], value[3], value[4])
        for value in get_export_history(site):
            print '"%s","%s","%s","%s","%s"' % (value[0], value[1], value[2], value[3], value[4])

    print >> sys.stderr, '# End: ProductsUp report: %s' % (datetime.datetime.now().time().isoformat())


if __name__ == '__main__':
    main(sys.argv)
