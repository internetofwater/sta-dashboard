FROM python:3.7.10-stretch
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt

CMD ["./docker_entrypoint.sh"] 