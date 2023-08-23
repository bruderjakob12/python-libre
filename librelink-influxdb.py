import os
import json
import requests
import pytz
import datetime
import time
import traceback
from dateutil import parser
from librelink import LibreLink

INFLUX_ADDRESS = os.environ['INFLUX_ADDRESS']
l = LibreLink(os.environ['LIBRE_EMAIL'], os.environ['LIBRE_PASSWORD'])


def libre_time_to_utc(libre_timestamp):
    loc = pytz.timezone('UTC').localize(parser.parse(libre_timestamp)).timestamp()
    return int(loc)


def influx_time_to_utc(influx_timestamp):
    return int(parser.parse(influx_timestamp).timestamp())


def write_influx_string(libre_timestamp, value, sensor_id=None, historic=False):
    unixtime = libre_time_to_utc(libre_timestamp)
    his = ',historic=no'
    sens = ''
    if historic:
        his = ',historic=yes'
    if sensor_id is not None:
        sens = ',sensor_id='+sensor_id
    sensor_data = 'freestyle'+his+sens+' sugar='+str(value) + ' ' + str(int(unixtime))
    try:
        r = requests.post('http://' + INFLUX_ADDRESS + '/write?db=sensors&precision=s', data=sensor_data)
    except:
        print(traceback.print_exc())


def influx_get_data():
    influx_keys = {}
    try:
        r = requests.get('http://' + INFLUX_ADDRESS + '/query?db=sensors', params='q=SELECT "sugar" FROM "freestyle" WHERE time >= now() - 13h ORDER BY time').json()
        for val in r['results'][0]['series'][0]['values']:
            influx_keys[influx_time_to_utc(val[0])] = val[1]
        return influx_keys
    except:
        print('No historic data found')
        return influx_keys
    

while True:
    data = l.get_data()
    write_influx_string(data['data']['connection']['glucoseMeasurement']['FactoryTimestamp'], data['data']['connection']['glucoseMeasurement']['Value'], data['data']['connection']['sensor']['sn'])
    influx_keys = influx_get_data()
    
    for item in data['data']['graphData']:
        key = libre_time_to_utc(item['FactoryTimestamp'])
        if key not in influx_keys.keys():
            # we only write the "graph" data if these values are missing.
            write_influx_string(item['FactoryTimestamp'], item['Value'], None, True)
            print(item['Timestamp'])
            print(key)
            print(item['Value'])
    time.sleep(45)
    
