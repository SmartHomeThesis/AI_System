# This is a sample Dockerfile you can modify to deploy your own app based on face_recognition

FROM python:3.9-slim-bullseye

RUN apt-get -y update
RUN apt-get install -y --fix-missing \
    build-essential \
    cmake \
    gfortran \
    git \
    wget \
    curl \
    graphicsmagick \
    libgraphicsmagick1-dev \
    libatlas-base-dev \
    libavcodec-dev \
    libavformat-dev \
    libgtk2.0-dev \
    libjpeg-dev \
    liblapack-dev \
    libswscale-dev \
    pkg-config \
    python3-dev \
    python3-numpy \
    software-properties-common \
    zip \
    python3-dev \
    python3-numpy \
    software-properties-common \
    zip \
    libasound-dev libportaudio2 libportaudiocpp0 \
    libpulse0 libasound2 libasound2-plugins\
    portaudio19-dev\
    python3-tk\
    pulseaudio \
    vlc \
    vim \
    libgirepository1.0-dev \
    alsa-utils \
    python3-gst-1.0 \
    net-tools \
    && apt-get clean && rm -rf /tmp/* /var/tmp/*

RUN cd ~ && \
    mkdir -p dlib && \
    git clone -b 'v19.9' --single-branch https://github.com/davisking/dlib.git dlib/ && \
    cd  dlib/ && \
    python3 setup.py install --yes USE_AVX_INSTRUCTIONS


# The rest of this file just runs an example script.



COPY . /root/face_recognition
RUN cd /root/face_recognition && \
    pip3 install -r requirements.txt 

# Add pip3 install opencv-python==4.1.2.30 if you want to run the live webcam examples

CMD cd /root/face_recognition/ && \
    python3 main.py