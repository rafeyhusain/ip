## To run the script:
Run:
```
php cleanData.php --force --min 200 --max 300 --output outputFolder
```

if you run the script once, you dont need to use --force the second time.

To check the options run:
```
php cleanData.php --help 
```
which will show the help:
> --force : Fresh force

> --min   : Min Threshold, should provide value 

> --max   : Max Threshold, should provide value 

> --second-level   : Max Threshold, should provide value 

> --output   : Output folder 

> --help   : Help List 


### In order to run the script above :
You need the file database.csv, which can be obtained by running the command below:
```
es2csv -s 50000 -i product_sg -D product -f category.url masterbrain -r -q @'query.json' --verify-certs -u https://iprice:fGcXoXcBtYaWfUpE@es-qa.ipricegroup.com:443 -o database.csv
```
to change the country, all you have to do is change product_sg to ex. product_my
#### Play with the data
Query that is fetched above in the es2csv command is inside the query.json, you can play around with it in that file before running es2csv command above.

## dependencies 
- es2csv : https://github.com/taraslayshchuk/es2csv
- PHP : RainbowLand website! (Abidul istuupid)
