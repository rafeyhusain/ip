## To run the script:
Run:
php cleanData.php --force --min 200 --max 300 --output outputFolder

if you run the script once, you dont need to use --force the second time.

To check the options run:
php cleanData.php --help 


In order to run the script above, you need the file database.csv, which can be obtained by running the command below:
es2csv -s 50000 -i product_sg -D product -f category.url masterbrain -r -q @'query.json' --verify-certs -u https://iprice:fGcXoXcBtYaWfUpE@es-qa.ipricegroup.com:443 -o database.csv

to change the country, all you have to do is change product_sg to ex. product_my

