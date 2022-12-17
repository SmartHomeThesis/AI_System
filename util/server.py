from Adafruit_IO import MQTTClient
from dotenv import load_dotenv
import serial.tools.list_ports
import util.physical as physical
import sys
import serial
import os
import time

AIO_FEED_DEVICE = ["smart-home.temperature", "smart-home.humidity", "smart-home.light", "smart-home.door", "smart-home.face-recognition"]

load_dotenv()

AIO_USERNAME = "HuuHanh"
AIO_KEY = "aio_huRY07EQl9luPKKGMgRG1WIqy5OJ"

isDoorSignal = False
isDoor = False
isLightSignal = False
isLight = False
count = 0

def connected(client):
    for feed in AIO_FEED_DEVICE:
        client.subscribe(feed)

def disconnected(client):
    sys.exit(1)

def message(client, feed_id, payload):  
     if feed_id == "smart-home.door":
        global isDoorSignal, isDoor
        isDoorSignal = True
        if payload == "1":
            isDoor = True
        else:
            isDoor = False


client = MQTTClient(AIO_USERNAME, AIO_KEY)
client.on_connect = connected
client.on_disconnect = disconnected
client.on_message = message
client.connect()
client.loop_background()

def getPort():
    ports = serial.tools.list_ports.comports()
    N = len(ports)
    commPort = "None"
    for i in range(0, N):
        port = ports[i]
        strPort = str(port)
        if "USB Serial Port" in strPort:
            splitPort = strPort.split(" ")
            commPort = (splitPort[0])
    return commPort

portName = getPort()
if portName != "None":
    ser = serial.Serial(port=portName, baudrate=9600)
      
while True:
    if count == 100:
        print("***************************************************************")
        temp = physical.readTemperature(ser)/10
        print(f"Temperature: {temp}°C")
        client.publish("smart-home.temperature", temp)

        humid = physical.readHumidity(ser)/10
        print(f"Humidity: {humid}%")
        client.publish("smart-home.humidity", humid)
        count = 0
        
    if isDoorSignal:
        print(isDoorSignal, isDoor)
        if isDoor:
            physical.setDevice1(True, ser)
        else:
            physical.setDevice1(False, ser)
        isDoorSignal = False

    count += 1
    time.sleep(0.1)