FROM gitpod/workspace-full

RUN sudo apt-get update \
    && sudo apt-get install -y --no-install-recommends \
        tree \
        mediainfo \
        neofetch \
        ffmpeg \
        libasound2-dev \
        libgtk-3-dev \
        libnss3-dev \
        curl \
        git \
        gnupg2 \
        unzip \
        wget \
        jq && \
        sudo rm -rf /var/lib/apt/lists/*

RUN curl -sO https://cli-assets.heroku.com/install.sh && bash install.sh && rm install.sh