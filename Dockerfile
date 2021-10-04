FROM python:3.7.10-stretch
WORKDIR /app
ADD . /app
RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["sh", "./docker-entrypoint.sh"] 