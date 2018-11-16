# takes the category tree list and creates a batchfile with the first level cats
# add 'ES_get_products_by_category.py " ' before each category and ' " 5000' to query for 5000 products
# run batchfile from commandline


import csv
import sys

reload(sys)
sys.setdefaultencoding("utf-8")

filename = "categories_tree_english.csv"
outputfile = "get_firstlevel_products_by_category.bat"
output = []
with open(filename, 'rb') as csvfile:
    rows = csv.reader(csvfile, delimiter=',')
    for row in rows:
        if '/' in row[0]:
            output.append(row[0].split('/')[0])
    output = set(output)
with open(outputfile, 'w') as file:
    writer = csv.writer(file, delimiter=',', lineterminator='\n')
    for row in output:
        writer.writerow([row])
