FROM ubuntu:latest

COPY requirements.txt /

# https://serverfault.com/a/992421 for tzdata
RUN apt-get update \
    && DEBIAN_FRONTEND="noninteractive" apt-get install -y \
       tzdata \
       vim \
       wget \
       unzip \
       python3 \
       libnss3 \
       libgconf-2-4 \
       libxi6 \
       python3-pip \
    && pip3 install --upgrade pip \
    && pip install -r requirements.txt

# download chromedriver and move to path
RUN wget \
    https://chromedriver.storage.googleapis.com/81.0.4044.69/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip \
    && rm chromedriver_linux64.zip \
    && mv chromedriver /usr/local/bin/chromedriver

# Install Chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN dpkg -i google-chrome-stable_current_amd64.deb; apt-get -fy install

ARG FROM_ADDR
ARG EMAIL_PASSWORD

ENV FROM_ADDR=${FROM_ADDR}
ENV EMAIL_PASSWORD=${EMAIL_PASSWORD}

COPY subscribers.json /
COPY script.py /

ENTRYPOINT python3 script.py
