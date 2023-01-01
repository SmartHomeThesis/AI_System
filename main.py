from authenticate import FaceRecognition
from voice_bot import speaker_verification
from voice_bot.voice_recognition import run_voice_bot
from util.physical import getPort
from Adafruit_IO import MQTTClient
from dotenv import dotenv_values
import serial.tools.list_ports
import sys
import serial
import time


# connect to Adafruit IO
isDoorSignal = False
isDoor = False
isLightSignal = False
isLight = False
count = 0

AIO_FEED_DEVICE = ["smart-home.temperature", "smart-home.humidity", "smart-home.light", "smart-home.door", "smart-home.face-recognition"]

config = dotenv_values('./.env')
AIO_USERNAME = config.get('USERNAME')
AIO_KEY = config.get('API_KEY')


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


# connect to Jetson Nano
portName = getPort()
if portName != "None":
    ser = serial.Serial(port=portName, baudrate=9600)

def countdown(t):

    while t:
        mins, secs = divmod(t, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        print(timer, end="\r")
        time.sleep(1)
        t -= 1


fr = FaceRecognition()

print("*************************************************************************")
print("*             Welcome to our system. Plese select user type             *")
print("* 1. Already have acount                                                *")
print("* 2. New user                                                           *")
print("*************************************************************************")
user_choice = int(input())

if user_choice == 1:
    authentication, name = fr.run_recognition()
    if authentication == True:
        client.publish("smart-home.face-recognition", name)   
        run_voice_bot()
elif user_choice == 2:
    # Voice flow 
    print("*************************************************************************")
    print("* The system will record your voice 5 times, 5 seconds each time. Recording will take place later")
    countdown(3)
    print("*************************************************************************")
    # 1. Record user voice (5 samples)
    speaker_verification.record_sample() 
    # Train model (voice)
    speaker_verification.train_model()
else:   
    exit()
