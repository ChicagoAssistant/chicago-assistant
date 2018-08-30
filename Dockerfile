FROM python:3.5

WORKDIR /

COPY requirements.txt /

RUN pip install -r requirements.txt

RUN python -m spacy download en_core_web_md

RUN python -m spacy link en_core_web_md en
