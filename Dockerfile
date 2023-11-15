FROM public.ecr.aws/docker/library/ubuntu:22.04

## CPU DOCKERFILE

ENV BLENDER_VERSION 4.0
ENV BLENDER_VERSION_MAJOR 4.0.0
ENV BLENDER_URL https://mirror.clarkson.edu/blender/release/Blender${BLENDER_VERSION}/blender-${BLENDER_VERSION_MAJOR}-linux-x64.tar.xz


# Install dependencies
RUN apt-get update -y && \
    apt-get install -y \
    sudo \
    curl \
    ca-certificates \
    zip \
    xz-utils \
    python3 \
    python3-pip 

# Download and install AWS CLI
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    sudo ./aws/install && \
    rm ./aws/install

# Download and install Blender
RUN curl "${BLENDER_URL}" -o "blender.tar.xz" && \
    tar -xvf blender.tar.xz --strip-components=1 -C /bin && \
    rm -rf blender.tar.xz && \
    rm -rf blender

RUN apt-get update -y && \
    apt-get install -y \
    libx11-dev \
    libxi-dev \
    libxxf86vm-dev \
    libfontconfig1 \
    libxrender1 \
    libgl1-mesa-glx \
    libxkbcommon-x11-0 \
    libsm6 

RUN pip3 install boto3
RUN pip install requests


# Copy the script to the root of the container and give it permission to be executed

COPY ./render.py /
COPY ./app.py /
COPY ./cameras_ngp.py /
COPY ./batch_scene.blend /

RUN chmod +x /render.py
RUN chmod +x /app.py
RUN chmod +x /batch_scene.blend
RUN chmod +x /cameras_ngp.py


WORKDIR /

ENTRYPOINT ["python3", "/app.py"]
 