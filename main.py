import json
import os
import sys
import threading
import time
import urllib.request


import requests
from Adafruit_IO import MQTTClient
from dotenv import dotenv_values


from authentication import FaceRecognition
from speaker_verification import record_sample, test_model, train_model
from util import countdown, getPort, readSerial, record_audio, speech_to_text, text_to_speech
from voice_bot.physical import (readHumidity, readTemperature, setDevice1,
                                setDevice2)


# Declare Adafruit IO components - Start
config = dotenv_values(".env")
AIO_KEY = config.get('AIO_KEY')
AIO_USERNAME = config.get('AIO_USERNAME')
AIO_FEED_DEVICE = ["smart-home.temperature", "smart-home.humidity", "smart-home.light", "smart-home.door", "smart-home.face-recognition"]


def connected(client):
    for feed in AIO_FEED_DEVICE:
        client.subscribe(feed)

def message(client, feed_id, payload):
    if feed_id == AIO_FEED_DEVICE[2]:
        if payload == "0":
            setDevice2(False, ser)
        if payload == "1":
            setDevice2(True, ser)
    if feed_id == AIO_FEED_DEVICE[3]:
        if payload == "0":
            setDevice1(False, ser)
        if payload == "1":
            setDevice1(True, ser)        

def disconnected():
    sys.exit(1)


client = MQTTClient(AIO_USERNAME, AIO_KEY)
client.on_connect = connected
client.on_disconnect = disconnected
client.on_message = message
client.connect()
client.loop_background()
# Declare Adafruit IO components - End


# Connect to USB port 
ser = getPort()
# Face Recognition
fr = FaceRecognition()


def control_device(bot_message, ser):
    if "đèn" in bot_message:
        if "tắt" in bot_message:
            client.publish("smart-home.light", 0)
        else:
            client.publish("smart-home.light", 1)
    else:
        if "mở" in bot_message:
            client.publish("smart-home.door", 1)
        else:
            client.publish("smart-home.door", 0)


def run_voice_bot():
    bot_message = "Cozy xin chào"
    text_to_speech(bot_message)
    

    while bot_message != "Tạm biệt":
        bot_message = ""
        
        
        # record_audio()
        # username = test_model("user.wav")
        # user_message = speech_to_text("user.wav")s
        # os.remove("user.wav")

        username = "Hanh"
        user_message = "Tắt cửa phòng khách"

        if username != "Unknown" and user_message is not None:
            print(username + ": {}".format(user_message))
            user = json.loads(urllib.request.urlopen(f"https://backend-production-a7e0.up.railway.app/api/utils/user-permission/{username}").read())

            start = time.time()
            if user["permission"]:
                for permission in user["permission"]:
                    if permission.lower() in user_message or user["permission"] == "All":
                        r = requests.post('http://localhost:5002/webhooks/rest/webhook', json={"message": user_message})
        
                        for i in r.json():
                            bot_message = i["text"]
                            control_device(bot_message, ser)
                            text_to_speech(bot_message) 
                        
                        print("Bot: " + f"{bot_message}")
                        print("*************************************************************************")
                        end = time.time()
                        print(end-start)
                        break
                    else: 
                        text_to_speech("Không thể thực hiện hành động này")
                        break
            else:
                text_to_speech("Không thể thực hiện hành động này")    
        else:
            text_to_speech("Không thể thực hiện hành động này") 

     

        

 
       
                   
def handle_sensor():
    count = 0
    while True:
        if count == 60:
            value_temp = readSerial(client, ser)/10
            client.publish("smart-home.temperature", value_temp)
            # value_humid = readHumidity(ser)/10
            # client.publish("smart-home.humidity", value_humid)
            count = 0

        count += 1
        time.sleep(1)


def handle_AI():
    while True:
        print("*************************************************************************")
        print("*                         Welcome to our system                         *")
        print("* 1. Login                                                              *")
        print("* 2. Register                                                           *")
        print("*************************************************************************\n")
        user_choice = int(input())

        if user_choice == 1:
            authentication, name = fr.run_recognition()
            if authentication == True:
                client.publish("smart-home.face-recognition", name) 
                client.publish("smart-home.door", 1) 
                setDevice1(True, ser) 
                run_voice_bot()
        elif user_choice == 2:
            name = input("Enter your name: ")

            # Face flow
            print("*************************************************************************")
            print("************* Take 5 pictures to train model (Press Space) **************")
            print("*************************************************************************\n")
            countdown(5)
            fr.take_picture(name)
            fr.train_model()

            # Voice flow 
            print("*************************************************************************")
            print("************ Record your voice 5 times (5 seconds each time) ************")
            print("*************************************************************************\n")
            countdown(5)
            record_sample(name) 
            train_model()
        else:   
            exit()

def product():
    t1 = threading.Thread(target=handle_sensor, name='t1')
    t2 = threading.Thread(target=handle_AI, name='t2')

    t1.start()
    t2.start()

    t1.join()
    t2.join()

run_voice_bot()
# handle_sensor()
