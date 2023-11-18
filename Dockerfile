#Deriving the ubuntu base image
FROM ubuntu:20.04

EXPOSE 80

USER root

ENV DEBIAN_FRONTEND noninteractive

RUN mkdir /opt/boehringeringelheim
RUN apt-get update && apt-get install -y --no-install-recommends apt-utils
RUN apt-get install -y ffmpeg
RUN apt-get install -y build-essential libssl-dev ca-certificates libasound2 wget


WORKDIR /opt/boehringeringelheim

COPY ./requirements.txt ./requirements.txt

# Virtual Env
ENV VIRTUAL_ENV=/opt/venv
RUN apt-get install -y python3.10
RUN apt-get install -y python3-pip && python3 -m pip install --upgrade pip && python3 -m pip install virtualenv && virtualenv --python python3 $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
# Install dependencies
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install -r requirements.txt
RUN python3 -m pip freeze

# Copy repo folder to working directory
COPY ./ ./

RUN chmod a+x src/run.sh

CMD ["./src/run.sh"]
