FROM python:3.10

EXPOSE 80

USER root

RUN mkdir /opt/boehringeringelheim

WORKDIR /opt/boehringeringelheim

COPY ./requirements.txt ./requirements.txt

# Install dependencies
RUN pip install -r requirements.txt

# Copy repo folder to working directory
COPY ./ ./

RUN chmod a+x src/run.sh

CMD ["./src/run.sh"]