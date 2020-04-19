FROM centos:7
RUN yum -y install epel-release
RUN yum -y install https://centos7.iuscommunity.org/ius-release.rpm
RUN yum -y update

RUN yum -y install nginx bash vim netcat curl wget less vim net-tools iproute supervisor mariadb-devel nc gcc scp rsync mariadb python36u python36u-pip python36u-devel
RUN yum clean all

RUN pip3 install --upgrade pip

COPY ./avanti/ /opt/app/avanti
COPY ./requirements.txt /opt/app/requirements.txt

WORKDIR /opt/app
RUN pip3 install -r /opt/app/requirements.txt

COPY ./deploy/config.yaml /opt/app/config.yaml
COPY ./deploy/nginx.conf /etc/nginx/nginx.conf
COPY ./deploy/supervisord.conf /etc/supervisord.conf
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN mkdir -p /etc/nginx/ssl/ /var/log/avanti/
COPY ./ssl/ /etc/nginx/ssl/

ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ARG DB_NAME=avanti
ARG DB_USER=avanti
ARG DB_PASS=password
ARG DB_HOST=localhost
ARG PYTHONPATH=/opt/app/


ENV DB_NAME="${DB_NAME}"
ENV DB_USER="${DB_USER}"
ENV DB_PASS="${DB_PASS}"
ENV DB_HOST="${DB_HOST}"
ENV PYTHONPATH="${PYTHONPATH}"

ENTRYPOINT ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
