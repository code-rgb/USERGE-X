
FROM gitpod/workspace-full

RUN sudo apt-get update \
    && sudo apt-get install -y --no-install-recommends \
        tree \
        wget2 \
        pv \
        p7zip-full \
        mediainfo \
        neofetch \
        ffmpeg \
    && sudo rm -rf /var/lib/apt/lists/*

RUN curl https://cli-assets.heroku.com/install.sh | sh
