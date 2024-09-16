FROM mirror.gcr.io/python:3.11

WORKDIR /app
COPY requirements.txt /app
RUN pip3 install -r requirements.txt --no-cache-dir

EXPOSE 8080

COPY . /app
RUN chmod +x ./start.sh
CMD ./start.sh

ENV TZ Europe/Moscow
ENV PYTHONUNBUFFERED=1
