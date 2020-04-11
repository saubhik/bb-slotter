FROM ubuntu:latest

COPY script.py requirements.txt /

RUN apt-get update \
    && apt-get install -y vim wget unzip python3 libnss3 libgconf-2-4 libxi6 python3-pip \
    && pip3 install --upgrade pip \
    && pip install -r requirements.txt

# download chromedriver and move to path
RUN wget https://chromedriver.storage.googleapis.com/81.0.4044.69/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip \
    && rm chromedriver_linux64.zip \
    && mv chromedriver /usr/local/bin/chromedriver

# Install Chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN dpkg -i google-chrome-stable_current_amd64.deb; apt-get -fy install

ARG FROM_ADDR
ARG TO_ADDR
ARG EMAIL_PASSWORD
ARG CITY1
ARG CITY2
ARG AREA1
ARG AREA2
ARG URL

ENV FROM_ADDR=$FROM_ADDR
ENV TO_ADDR=$TO_ADDR
ENV EMAIL_PASSWORD=$EMAIL_PASSWORD
ENV CITY1=$CITY1
ENV CITY2=$CITY2
ENV AREA1=$AREA1
ENV AREA2=$AREA2
ENV URL=$URL

ENTRYPOINT python3 script.py
