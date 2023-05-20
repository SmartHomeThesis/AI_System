import json
import os
import sys
import urllib.request


import requests
import keyboard
from Adafruit_IO import MQTTClient
from dotenv import dotenv_values
from authentication import FaceRecognition


from speaker_verification import record_sample, test_model, train_model
from util import *


# Declare Adafruit IO components - Start
config = dotenv_values(".env")
AIO_KEY = config.get('AIO_KEY')
AIO_USERNAME = config.get('AIO_USERNAME')
AIO_FEED_DEVICE = ["smart-home.temperature", "smart-home.humidity", "smart-home.light-livingroom", "smart-home.light-bedroom", "smart-home.door", "smart-home.face-recognition"]


def connected(client):
    for feed in AIO_FEED_DEVICE:
        client.subscribe(feed)

def message(client, feed_id, payload):
    # Connect to USB port 
    ser = getPort() 
    if feed_id == AIO_FEED_DEVICE[2]:
        if payload == "0":
            setDevice2(False, ser)
        if payload == "1":
            setDevice2(True, ser)
    elif feed_id == AIO_FEED_DEVICE[3]:
        if payload == "0":
            setDevice1(False, ser)
        if payload == "1":
            setDevice1(True, ser)      
    elif feed_id == AIO_FEED_DEVICE[4]:   
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


def control_device(msg):
    if "khách" in msg:
        if "tắt" in msg and "đèn" in msg:
            client.publish("smart-home.light-livingroom", 0)
        else:
            client.publish("smart-home.light-livingroom", 1)
    elif "ngủ" in msg:
        if "tắt" in msg and "đèn" in msg:
            client.publish("smart-home.light-bedroom", 0)
        else:
            client.publish("smart-home.light-bedroom", 1)
    else:      
        if "đóng" in msg and "cửa" in msg:
            client.publish("smart-home.door", 0)
        else:
            client.publish("smart-home.door", 1)



def run_voice_bot():
    text_to_speech("Cozy xin chào")
    
    bot_message = ""
    while bot_message != "Tạm biệt":
        bot_message = ""    

        record_audio()
        username = test_model("user.wav")
        user_message = "None" if speech_to_text("user.wav") is None else speech_to_text("user.wav").lower()
        os.remove("user.wav")
    
        print(username + ": {}".format(user_message))
       
        if username != "Unknown" and user_message != "None":
            if "bật" in user_message or "mở" in user_message or "đóng" in user_message or "tắt" in user_message:
                domain = "https://backend-production-a7e0.up.railway.app"
                permission = urllib.request.urlopen(f"{domain}/api/utils/user-permission/{username}").read()
                user = json.loads(permission)

                if user["permission"]:
                    for permission in user["permission"]:
                        if permission.lower() in user_message or user["permission"] == "All":
                            control_device(user_message)
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
        text_to_speech("Chào mừng bạn đến với hệ thống của chúng tôi. Nếu bạn đã có tài khoản, xin vui lòng nhấn phím 1, nếu chưa có tài khoản, xin vui lòng nhấn phím 2.")

        if keyboard.read_key() == "1":
            # # Face Recognition
            # fr = FaceRecognition()
            # authentication, name = fr.run_recognition()
            # if authentication == True:
            #     client.publish("smart-home.face-recognition", name) 
            #     client.publish("smart-home.door", 1) 
            while True:
                text_to_speech("Hệ thống xác thực khuôn mặt thành công. Nếu muốn sử dụng trợ lý ảo, xin vui lòng nhấn phím 1")
                if keyboard.read_key() == "1":
                    run_voice_bot()
                else:
                    break
        elif keyboard.read_key() == "2":
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


if __name__ == '__main__':
    handle_AI()