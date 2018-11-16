# Purpose: This file can be used to generate FMT files using BCP
#
# Note: run this script when inside docker dir /tools/dataware-house/tests
#

rm -rf ./logs/errors.log
rm -rf ./logs/errors_bcp*.log

mkdir -p ./logs

#TABLES=('ga_acquisition' 'ga_conversions' 'ho_transactions' 'ho_performance' 'keyword_planner' 'search_console')
TABLES=('ga_acquisition')
SERVER='tcp:iprice-bi.database.windows.net'
DB='[test]'
USER_NAME='ipg'
PASSWORD='test12!@'

for table in "${TABLES[@]}"
do
        bcp $DB.dbo.$table format nul -n -f ../fmt/$table.fmt \
        -F2 -S $SERVER -U $USER_NAME -P $PASSWORD
done

rm ./nul