FROM python:3.5

MAINTAINER alexey shkil

RUN apt-get -y update

RUN apt-get install -y python-dev python-pip python3-pip

ADD requirments /home/requirments

RUN pip3 install -r /home/requirments