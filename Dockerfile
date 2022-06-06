FROM python:3.9-slim

USER root
WORKDIR /home/
COPY build/* build/
COPY requirements.txt requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
CMD python3 build/coursework.py