import requests
from time import sleep
from json import dumps, loads
from kafka import KafkaProducer

response = loads(requests.get("https://gbfs.fordgobike.com/gbfs/es/station_status.json").text)

print(response)