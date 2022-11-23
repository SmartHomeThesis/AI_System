from Adafruit_IO import MQTTClient
from dotenv import load_dotenv
import sys
import time
import json
import serial
import os

AIO_FEED_DEVICE = ["smart-home.fan", "smart-home.light"]

load_dotenv()

AIO_USERNAME = os.getenv("USERNAME")
AIO_KEY = os.getenv("API_KEY")


def connected(client):
    print("Connected successfully ...")
    for feed in AIO_FEED_DEVICE:
        client.subscribe(feed)


def subscribe(client, userdata, mid, granted_qos):
    print("Subscribed successfully ...")


def disconnected(client):
    print("Disconnect ...")
    sys.exit(1)


def message(client, feed_id, payload):  
    print (feed_id + ": " + payload)      


client = MQTTClient(AIO_USERNAME, AIO_KEY)
client.on_connect = connected
client.on_disconnect = disconnected
client.on_message = message
client.on_subscribe = subscribe
client.connect()
client.loop_background()

 
def processData(data):
    data = data.replace("!", "")
    data = data.replace("#", "")
    splitData = data.split(":")
    print(splitData)
    try:
        if splitData[0] == "1":
            if splitData[1] == "TEMP":
                client.publish("microbit-temp", splitData[2])
            elif splitData[1] == "HUMI":
                client.publish("microbit-humid", splitData[2])   
        elif splitData[0] == "2":
            if splitData[1] == "LIGHT":
                client.publish("microbit-light", splitData[2])   
        elif splitData[0] == "3":
            if splitData[1] == "GAS":
                client.publish("microbit-gas", splitData[2])               
    except: 
        pass        

mess = ""
def readSerial():
    bytesToRead = ser.inWaiting()
    if (bytesToRead > 0):
        global mess
        mess = mess + ser.read(bytesToRead).decode("UTF-8")
        while ("#" in mess) and ("!" in mess):
            start = mess.find("!")
            end = mess.find("#")
            processData(mess[start:end + 1])
            if (end == len(mess)):
                mess = ""
            else:
                mess = mess[end+1:]           