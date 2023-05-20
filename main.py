import json
import os
import sys
import time
import keyboard
import urllib.request


import requests
from Adafruit_IO import MQTTClient
from dotenv import dotenv_values


from authentication import FaceRecognition
from speaker_verification import record_sample, test_model, train_model
from util import countdown, getPort, record_audio, speech_to_text, text_to_speech
from voice_bot.physical import (setDevice1, setDevice2)


# Declare Adafruit IO components - Start
config = dotenv_values(".env")
AIO_KEY = config.get('AIO_KEY')
AIO_USERNAME = config.get('AIO_USERNAME')
AIO_FEED_DEVICE = ["smart-home.temperature", "smart-home.humidity", "smart-home.light-livingroom", "smart-home.light-bedroom", "smart-home.door", "smart-home.face-recognition"]


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
    if feed_id == AIO_FEED_DEVICE[4]:   
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


def control_device(msg):
    if "khách" in msg:
        if "tắt" in msg and "đèn" in msg:
            client.publish("smart-home.light-bedroom", 0)
        else:
            client.publish("smart-home.light-bedroom", 1)
    elif "ngủ":
        if "tắt" in msg and "đèn" in msg:
            client.publish("smart-home.light-livingroom", 0)
        else:
            client.publish("smart-home.light-livingroom", 1)
    else:      
        if "đóng":
            client.publish("smart-home.door", 0)
        else:
            client.publish("smart-home.door", 1)



def run_voice_bot():
    bot_message = "Cozy xin chào"
    text_to_speech(bot_message)
    

    while bot_message != "Tạm biệt":
        bot_message = ""
        
        
        record_audio()
        username = test_model("user.wav")
        user_message = speech_to_text("user.wav")
        
        if user_message is None:
            user_message = "None"

        user_message = user_message.lower()
        os.remove("user.wav")

        # username = "Hanh"
        # user_message = "Hà Nội thời tiết như thế nào"

        if user_message is not None:
            if "bật" in user_message or "mở" in user_message or "đóng" in user_message or "tắt" in user_message and username != "Unknown":
                print(username + ": {}".format(user_message))
                start = time.time()
                user = json.loads(urllib.request.urlopen(f"https://backend-production-a7e0.up.railway.app/api/utils/user-permission/{username}").read())
                if user["permission"]:
                    for permission in user["permission"]:
                        if permission.lower() in user_message or user["permission"] == "All":
                            control_device(user_message.lower())
                            end = time.time()
                            print(end-start)
                            break
                else:
                    text_to_speech("Không thể thực hiện hành động này")
            else:
                r = requests.post('http://localhost:5005/webhooks/rest/webhook', json={"message": user_message})
                for i in r.json():
                    bot_message = i["text"]
                    text_to_speech(bot_message)       

                    
def handle_AI():
    while True:
        print("*************************************************************************")
        print("*                            WELCOME TO COZY                            *")
        print("* 1. Login                                                              *")
        print("* 2. Register                                                           *")
        print("*************************************************************************\n")
        user_choice = int(input())

        if user_choice == 1:
            authentication, name = fr.run_recognition()
            if authentication == True:
                client.publish("smart-home.face-recognition", name) 
                client.publish("smart-home.door", 1) 
                while True:
                    if keyboard.is_pressed("a"):
                        run_voice_bot()
                    elif keyboard.is_pressed("q"):
                        break
        elif user_choice == 2:
            name = input("Enter your name: ")

            # # Face flow
            # print("*************************************************************************")
            # print("************* Take 5 pictures to train model (Press Space) **************")
            # print("*************************************************************************\n")
            # countdown(5)
            # fr.take_picture(name)
            # fr.train_model()

            # Voice flow 
            print("*************************************************************************")
            print("************ Record your voice 10 times (5 seconds each time) ***********")
            print("*************************************************************************\n")
            countdown(5)
            record_sample(name) 
            train_model()
        else:   
            exit()


# if __name__ == '__main__':
#     handle_AI()
run_voice_bot()
