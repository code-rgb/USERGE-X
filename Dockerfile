# set base image (host OS) [Debian Slim Buster]
FROM python:3.9-slim-buster

# https://shouldiblamecaching.com/
ENV PIP_NO_CACHE_DIR 1

# fix "ephimeral" / "AWS" file-systems
RUN sed -i.bak 's/us-west-2\.ec2\.//' /etc/apt/sources.list

# set the working directory in the container
WORKDIR /app/

RUN apt -qq update && apt -qq upgrade -y 
RUN apt -qq install -y --no-install-recommends \
    apt-utils \
    curl \
    git \
    gnupg2 \
    wget \
    unzip

# to resynchronize the package index files from their sources.
RUN apt -qq update

# http://bugs.python.org/issue19846
# https://github.com/SpEcHiDe/PublicLeech/pull/97
ENV LANG C.UTF-8

# we don't have an interactive xTerm
ENV DEBIAN_FRONTEND noninteractive

# install chrome
RUN mkdir -p /tmp/ && \
    cd /tmp/ && \
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    # -f ==> is required to --fix-missing-dependancies
    dpkg -i ./google-chrome-stable_current_amd64.deb; apt -fqqy install && \
    # clean up the container "layer", after we are done
    rm ./google-chrome-stable_current_amd64.deb

# install chromedriver
RUN mkdir -p /tmp/ && \
    cd /tmp/ && \
    wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE)/chromedriver_linux64.zip  && \
    unzip /tmp/chromedriver.zip chromedriver -d /usr/bin/ && \
    # clean up the container "layer", after we are done
    rm /tmp/chromedriver.zip

ENV GOOGLE_CHROME_DRIVER /usr/bin/chromedriver
ENV GOOGLE_CHROME_BIN /usr/bin/google-chrome-stable

# install required packages
RUN apt -qq install -y --no-install-recommends \
    # this package is required to fetch "contents" via "TLS"
    apt-transport-https \
    # install coreutils
    build-essential coreutils jq pv \
    # install gcc [ PEP 517 ]
    gcc \
    # install encoding tools
    ffmpeg mediainfo \
    # miscellaneous
    neofetch \
    # Pillow utils
    libfreetype6-dev libjpeg-dev libpng-dev libgif-dev libwebp-dev \
    python3-dev zlib1g-dev && \
    # clean up the container "layer", after we are done
    rm -rf /var/lib/apt/lists /var/cache/apt/archives /tmp/*

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies

RUN pip install -U setuptools setuptools-scm wheel && pip install --no-cache-dir -r requirements.txt

# copy the content of the local src directory to the working directory
COPY . .

# command to run on container start
CMD [ "bash", "./run" ]
