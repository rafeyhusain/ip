FROM docker.elastic.co/logstash/logstash:5.5.3
USER root
RUN mkdir -p /var/log/logstash
RUN chown -R logstash:logstash /var/log/logstash
USER logstash

ADD ./config/share.config/* /usr/share/logstash/config/
RUN logstash-plugin remove x-pack
