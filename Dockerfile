FROM python:3.9
MAINTAINER James Haller <jameshaller27@gmail.com>

RUN mkdir -p /app
COPY . /app
WORKDIR /app

RUN pip install -r ../requirements.txt
CMD python -u main.py
