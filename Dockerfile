FROM python:3.7.10-stretch

WORKDIR /app

ADD . /app

RUN pip install -r requirements.txt

EXPOSE 8080

CMD ["flask", "run", "-h", "0.0.0.0"]