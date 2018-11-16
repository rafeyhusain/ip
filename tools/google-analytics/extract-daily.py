import pandas, sys, argparse, os
from datetime import date, datetime

argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('query', type=str, help=('Query file name).'))
argparser.add_argument('date', type=int, help=('Date for report).'))
argparser.add_argument('output', type=str, help=('Output folder).'))


def main(argv):
    args = argparser.parse_args()

    print >> sys.stderr, '# Start: Extract Process: %s, %s, %s' % (
        args.query, args.date, datetime.now().time().isoformat())

    report_csv = args.output + "/" + args.query + ".csv"

    output = pandas.read_csv(report_csv)

    output = output[output['ga:date'] == args.date]

    output.to_csv(sys.stdout,
                  header=True,
                  index=False,
                  encoding='utf-8-sig',
                  sep='\t')

    print >> sys.stderr, '# End: Extract Process: %s, %s, %s' % (
        args.query, args.date, datetime.now().time().isoformat())


if __name__ == '__main__':
    main(sys.argv)
