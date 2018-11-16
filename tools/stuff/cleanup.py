#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse, codecs, datetime, pandas, re, sys, os, time

reload(sys)
sys.setdefaultencoding("UTF-8")

argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('file', type=str, help=('File with one keyword per line.'))


def main(argv):
    args = argparser.parse_args()

    csv = pandas.read_csv(args.file, error_bad_lines=False)

    re1, re2, re3, re4 = re.compile("[\[\]\(\)<>/|\\{}?\",]+"), re.compile("^[!@#$%^&*,\.\-\+\s\"]+"), re.compile(
        "[!@#$%^&*,\.\-\+\s\"]+$"), re.compile("[\s]+")
    for index, line in csv.iterrows():
        value = str(line[1])
        value = re4.sub(" ", value)  # multiple spaces
        value = re1.sub("", value)  # (), [], <>, /|\, {}, ?, " anywhere
        value = re2.sub("", value)  # !@#$%^&*,. at the beginning
        value = re3.sub("", value)  # !@#$%^&*,. at the end
        # � has to be done manually
        csv.at[index, "keyword"] = value

    uniques = {}
    duplicates = []
    for index, line in csv.iterrows():
        a, b, c = str(line[2]), str(line[3]), str(line[4])
        if a != "0" and b != "nan" and c != "nan":
            value = a + b + c
            if value not in uniques:
                uniques[value] = 1
            else:
                duplicates.append(index)

    csv.drop(duplicates, inplace=True)

    csv.to_csv(sys.stdout, header=True, index=False, encoding='utf-8-sig')


if __name__ == '__main__':
    main(sys.argv)
