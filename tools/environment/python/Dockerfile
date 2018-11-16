FROM phusion/baseimage
ARG ENV
ENV PATH="/opt/mssql-tools/bin:${PATH}"
ADD ./crontab-${ENV} /etc/crontab
ADD ./xvfb /etc/init.d/xvfb
ADD ./geckodriver /usr/local/bin/geckodriver
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/ubuntu/16.04/prod.list | tee /etc/apt/sources.list.d/msprod.list
RUN apt-get update
RUN ACCEPT_EULA=Y apt-get install -y cron wget vim python2.7 python-pip npm xvfb firefox mssql-tools
RUN ln -s "$(which nodejs)" /usr/bin/node
RUN chmod 0600 /etc/crontab
RUN chmod +x /etc/init.d/xvfb
RUN chmod +x /usr/local/bin/geckodriver
RUN pip install --upgrade pip
RUN pip install requests pandas progress elasticsearch selenium==3.6.0 suds xlrd Pillow xmljson python-firebase
RUN pip install google-api-python-client pytz lxml HTMLParser scrapy simplejson progressbar sklearn scipy googleads
RUN pip install awscli
RUN npm install -g elasticdump
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
RUN mkdir -p /srv/ftp/
CMD ["/sbin/my_init"]
