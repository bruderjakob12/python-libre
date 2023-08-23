FROM python:latest

WORKDIR /usr/local/bin
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY *.py *.pkl ./

CMD ["python3", "librelink-influxdb.py"]
