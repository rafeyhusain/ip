# Purpose: This file can be used to test csv_importer.
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
TABLES=('ga_acquisition' 'ga_conversions')
SERVER='tcp:iprice-bi.database.windows.net'
DB='[test]'
USER_NAME='ipg'
PASSWORD='test12!@'

# Note: Select folder below for tests you want to run 
# 'quick' = quick tests for one row
# 'long' = Production quality CSV

for table in "${TABLES[@]}"
do
      python ./../csv_importer/main.py \
      --db_server $SERVER\
      --db_name  $DB\
      --user_name $USER_NAME \
      --password $PASSWORD \
      "" \
      $table \
      ./csvt/importer/quick/$table.csvt \
      ./logs/errors.log \
  2>> ./logs/errors.log
done
