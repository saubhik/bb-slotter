FROM ubuntu:latest

COPY script.py requirements.txt subscribers.json /

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
ARG EMAIL_PASSWORD

ENV FROM_ADDR=${FROM_ADDR}
ENV EMAIL_PASSWORD=${EMAIL_PASSWORD}

ENTRYPOINT python3 script.py
