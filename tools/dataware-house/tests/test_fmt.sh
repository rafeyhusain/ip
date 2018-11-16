# Purpose: This file can be used to test FMT files independent of csv_importer
#
# Note: run this script when inside docker dir /tools/dataware-house/tests
#
# - Uploads one test row in table. 
# - Test row will have ipg:batchNo=TEST_FMT
# - logs will be generated inside dir /tools/dataware-house/tests/logs

rm -rf ./logs/errors.log
rm -rf ./logs/errors_bcp*.log

mkdir -p ./logs

#TABLES=('ga_acquisition' 'ga_conversions' 'ho_transactions' 'ho_performance' 'keyword_planner' 'search_console')
TABLES=('ga_acquisition')
SERVER='tcp:iprice-bi.database.windows.net'
DB='test'
USER_NAME='ipg'
PASSWORD='test12!@'

for table in "${TABLES[@]}"
do
        bcp $DB.dbo.$table in ./csvt/fmt/$table.csvt -b1000 -m100000 -F2 -c \
        -e './logs/errors_bcp_'$table'.log' \
        -S $SERVER -U $USER_NAME -P $PASSWORD
done
