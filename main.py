import os
import sys
import time
import threading
import requests
import playsound
from gtts import gTTS
from authentication import FaceRecognition
from util import getPort, countdown, speech_to_text, record_audio
from dotenv import dotenv_values
from Adafruit_IO import MQTTClient
from speaker_verification import test_model, record_sample, train_model
from voice_bot.physical import readHumidity, readTemperature, setDevice1, setDevice2


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
            setDevice2(False, ser)
            client.publish("smart-home.light", 0)
        else:
            setDevice2(True, ser)
            client.publish("smart-home.light", 1)
    else:
        if "mở" in bot_message:
            setDevice1(True, ser)
            client.publish("smart-home.door", 1)
        else:
            setDevice1(False, ser) 
            client.publish("smart-home.door", 0)

def run_voice_bot():
    # Start the conversation
    bot_message = "Xin chào"
    print("Bot: " + f"{bot_message}")
    audio = gTTS(bot_message, lang="vi", slow=False)
    playsound(audio)

    while bot_message != "Bye":
        bot_message = ""
        
        record_audio()
        user_name = test_model("user.wav")
        user_message = speech_to_text("user.wav")
        
        # Speaker verification 
        print(user_name + ": {}".format(user_message))
        r = requests.post('http://localhost:5002/webhooks/rest/webhook', json={"message": user_message})

        for i in r.json():
            if "False" in i["text"]:
                bot_message = i['text'][:i['text'].index(".")]
                control_device(bot_message, ser)
            else:
                bot_message = i["text"]
                playsound(bot_message) 
                   
            print("Bot: " + f"{bot_message}")
            print("*************************************************************************")





def handle_sensor():
    count = 0
    while True:
        if count == 30:
            value_temp = readTemperature(ser)/10
            client.publish("smart-home.temperature", value_temp)
            value_humid = readHumidity(ser)/10
            client.publish("smart-home.humidity", value_humid)
            count = 0

        count += 1

        time.sleep(1)

def handle_AI():
    while True:
        print("*************************************************************************")
        print("*             Welcome to our system. Plese select user type             *")
        print("* 1. Already have acount                                                *")
        print("* 2. New user                                                           *")
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

def main():
    t1 = threading.Thread(target=handle_sensor, name='t1')
    t2 = threading.Thread(target=handle_AI, name='t2')

    t1.start()
    t2.start()

    t1.join()
    t2.join()

main()