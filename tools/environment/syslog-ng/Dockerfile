FROM alpine:3.4

RUN apk add --update syslog-ng
ADD config/syslog-ng.conf /etc/syslog-ng/syslog-ng.conf

ENTRYPOINT ["/usr/sbin/syslog-ng", "-F"]
