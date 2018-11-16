## google-analytics:
Tool for downloading data from Google Analytics and imports them into csv files

##### Command:
- To download all analytics data from different countries and accept all queries from ```input/``` folder, run: 
```./download.sh``` 
- All csv files are saved in ```output/google-analytics/YmdHM``` and is mapped in ```/srv/ftp/google-analytics```
- ```client_secrets.json``` is a generated key from Google Analytics console

##### Resources:
- To read more about how to connect to Google Analytics see:
```https://developers.google.com/analytics/devguides/reporting/core/v3/quickstart/service-py```