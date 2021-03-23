FROM python:3.9-slim-buster

ENV PIP_NO_CACHE_DIR 1
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND noninteractive

RUN sed -i.bak 's/us-west-2\.ec2\.//' /etc/apt/sources.list

WORKDIR /app/

RUN apt -qq update && apt -qq upgrade -y && \
    apt -qq install -y --no-install-recommends \
    apt-utils \
    curl \
    git \
    gnupg2 \
    wget \
    unzip \
    tree

RUN mkdir -p /tmp/ && \
    cd /tmp/ && \
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg -i ./google-chrome-stable_current_amd64.deb; apt -fqqy install && \
    rm ./google-chrome-stable_current_amd64.deb

RUN mkdir -p /tmp/ && \
    cd /tmp/ && \
    wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE)/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip chromedriver -d /usr/bin/ && \
    rm /tmp/chromedriver.zip

ENV GOOGLE_CHROME_DRIVER /usr/bin/chromedriver
ENV GOOGLE_CHROME_BIN /usr/bin/google-chrome-stable

RUN apt -qq update && apt -qq install -y --no-install-recommends \
    gcc python3-dev zlib1g-dev \
    apt-transport-https \
    build-essential coreutils jq pv \
    ffmpeg mediainfo \
    neofetch \
    p7zip-full \
    libfreetype6-dev libjpeg-dev libpng-dev libgif-dev libwebp-dev && \
    rm -rf /var/lib/apt/lists /var/cache/apt/archives /tmp/*

COPY requirements.txt .

RUN pip install -U setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "bash", "./run" ]
