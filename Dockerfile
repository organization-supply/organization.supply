FROM python:3.7-buster
RUN mkdir /code
WORKDIR /code

# Add code to run
ADD . /code/

WORKDIR /code
RUN pip install -r requirements.txt

EXPOSE 80

ENTRYPOINT ["/bin/sh", "/code/docker-start.sh"]