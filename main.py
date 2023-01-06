import os
import sys
import time
import requests
import threading
import serial.tools.list_ports
import speech_recognition as sr
from dotenv import dotenv_values
from Adafruit_IO import MQTTClient
from authenticate import FaceRecognition
from speaker_verification import test_model, record_sample, train_model
from voice_recognition import text_to_speech, record_audio
from voice_bot.physical import readTemperature, readHumidity, setDevice1, setDevice2


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

def countdown(t):
    while t:
        mins, secs = divmod(t, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        print(timer, end="\r")
        time.sleep(1)
        t -= 1

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

def control_device(bot_message, ser):
    if "đèn" in bot_message:
        if "tắt" in bot_message:
            setDevice2(False, ser)
            client.publish("smart-home.light", 0)
        else:
            setDevice2(True, ser)
            client.publish("smart-home.light", 1)
    else:
        if "tắt" or "đóng" in bot_message:
            setDevice1(False, ser)
            client.publish("smart-home.door", 0)
        else:
            setDevice1(True, ser) 
            client.publish("smart-home.door", 1)

def run_voice_bot():
    # Start the conversation
    print("*******************************************************")
    bot_message = "Xin chào, bạn khỏe không?"
    print("Bot: " + f"{bot_message}")
    text_to_speech(bot_message)

    while bot_message != "Bye":
        bot_message = ""
        user_message = ""

        # User command
        record_audio()

        r = sr.Recognizer()
        with sr.AudioFile("user.wav") as source:
            try:
                audio = r.record(source)  # read the entire audio file
                user_message = (r.recognize_google(audio, language="vi")).lower()
            except:
                print("")    
        
        if len(user_message) == 0:
            continue
        
        # Speaker verification 
        print(test_model("user.wav") + ": {}".format(user_message))

        os.remove("user.wav")
        print("*******************************************************")

        r = requests.post('http://localhost:5002/webhooks/rest/webhook', json={"message": user_message})

        for i in r.json():
            if "False" in i["text"]:
                bot_message = i['text'][:i['text'].index(".")]
                control_device(bot_message, ser)
            else:
                bot_message = i["text"]
                text_to_speech(bot_message) 
                   
            print("Bot: " + f"{bot_message}")


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

fr = FaceRecognition()

def handle_sensor():
    count = 0
    while True:
        if count == 100:
            value_temp = readTemperature(ser)/10
            client.publish("smart-home.temperature", value_temp)
            value_humid = readHumidity(ser)/10
            client.publish("smart-home.humidity", value_humid)
            count = 0

        count += 1
        time.sleep(0.1)

def handle_AI():
    while True:
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

while True:
    t1 = threading.Thread(target=handle_sensor, name='t1')
    t2 = threading.Thread(target=handle_AI, name='t2')

    t1.start()
    t2.start()

    t1.join()
    t2.join()


    

