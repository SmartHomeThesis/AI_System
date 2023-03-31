import time
import wave
import pyaudio
import serial.tools.list_ports
import speech_recognition as sr
from authentication import FaceRecognition
import tkinter
import tkinter.messagebox
import customtkinter
import os
import sys
import time
import threading
import requests
import playsound
from gtts import gTTS
from authentication import FaceRecognition
from dotenv import dotenv_values
from Adafruit_IO import MQTTClient
from speaker_verification import test_model, record_sample, train_model
from voice_bot.physical import readHumidity, readTemperature, setDevice1, setDevice2

from voice_bot.physical import setDevice1

# Declare Adafruit IO components - Start
config = dotenv_values(".env")
AIO_KEY = config.get('AIO_KEY')
AIO_USERNAME = config.get('AIO_USERNAME')
AIO_FEED_DEVICE = ["smart-home.temperature", "smart-home.humidity", "smart-home.light", "smart-home.door", "smart-home.face-recognition"]


def connected(client):
    for feed in AIO_FEED_DEVICE:
        client.subscribe(feed)

# def message(client, feed_id, payload):
#     if feed_id == AIO_FEED_DEVICE[2]:
#         if payload == "0":
#             setDevice2(False, ser)
#         if payload == "1":
#             setDevice2(True, ser)
#     if feed_id == AIO_FEED_DEVICE[3]:
#         if payload == "0":
#             setDevice1(False, ser)
#         if payload == "1":
#             setDevice1(True, ser)        

def disconnected():
    sys.exit(1)


client = MQTTClient(AIO_USERNAME, AIO_KEY)
client.on_connect = connected
client.on_disconnect = disconnected
# client.on_message = message
client.connect()
client.loop_background()
# Declare Adafruit IO components - End


# Connect to USB port 

def countdown(t):
    while t:
        mins, secs = divmod(t, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        print(timer, end="\r")
        time.sleep(1)
        t-=1

def getPort():
    ports = serial.tools.list_ports.comports()
    N = len(ports)
    commPort = "None"
    ser = "None"
    for i in range(0, N):
        port = ports[i]
        strPort = str(port)
        if "USB Serial Port" in strPort:
            splitPort = strPort.split(" ")
            commPort = (splitPort[0])

    if commPort != "None":
        ser = serial.Serial(port=commPort, baudrate=9600)        
    return ser 

def record_audio():
    filename = "user.wav"
    chunk = 1024
    FORMAT = pyaudio.paInt16
    channels = 2
    sample_rate = 44100
    record_seconds = 3
    p = pyaudio.PyAudio()
    # open stream object as input & output
    stream = p.open(format=FORMAT,
                    channels=channels,
                    rate=sample_rate,
                    input=True,
                    frames_per_buffer=chunk)
    frames = []
    print("LISTENING")
    for i in range(0, int(sample_rate / chunk * record_seconds)):
        data = stream.read(chunk)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()
    wf = wave.open(filename, "wb")
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(sample_rate)
    wf.writeframes(b"".join(frames))
    wf.close()

def speech_to_text(audio):
    r = sr.Recognizer() 
    r.energy_threshold = 300
    r.dynamic_energy_threshold = False   
                                                                                   
    with sr.AudioFile(audio) as source:                  
        audio = r.record(source, duration=3)   
    try:
        return r.recognize_google(audio, language="vi")
    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))


def login_button_event():
    # Face Recognition
    fr = FaceRecognition()
    authentication, name = fr.run_recognition()
    if authentication == True:
        client.publish("smart-home.face-recognition", name) 
        client.publish("smart-home.door", 1) 
    # setDevice1(True, ser) 
