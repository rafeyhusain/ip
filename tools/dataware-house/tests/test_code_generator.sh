# Note: run this script when inside docker dir tools/dataware-house/tests
#
# This scipt generates FMT and SQL files based on templates available in
# csvx (for FMT) and sqlx (for SQL)

rm -rf ./logs/errors.log
rm -rf ./logs/*.csv

mkdir -p ./logs

python ./../code_generator/main.py \
  "./../code_generator/csvx" \
  "./../code_generator/sqlx" \
  "./../fmt/" \
  "./../sql/" \
  2>> ./logs/errors.log
