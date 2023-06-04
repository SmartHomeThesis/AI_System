import os
import time
import wave
from playsound import playsound
import pyttsx3

import pyaudio
import serial.tools.list_ports
import speech_recognition as sr
from gtts import gTTS


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
    record_seconds = 5
    micro_index = 1 
    p = pyaudio.PyAudio()
    # open stream object as input & output
    stream = p.open(format=FORMAT, channels=channels, rate=sample_rate, input=True, frames_per_buffer=chunk)
    frames = []

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
                                                                        
    with sr.AudioFile(audio) as source:                  
        audio = r.record(source, duration=3)   
    try:
        return r.recognize_google(audio, language="vi")
    except sr.UnknownValueError or sr.RequestError:
        return None

def text_to_speech(msg):
    audio = gTTS(msg, lang="vi", slow=False)
    audio.save("audio.mp3")
    playsound("audio.mp3")
    os.remove("audio.mp3")

relay1_ON  = [15, 6, 0, 0, 0, 255, 200, 164]
relay1_OFF = [15, 6, 0, 0, 0, 0, 136, 228]
def setDevice1(state, ser):
    if state == True:
        ser.write(relay1_ON)
    else:
        ser.write(relay1_OFF)

relay2_ON  = [0, 6, 0, 0, 0, 255, 200, 91]
relay2_OFF = [0, 6, 0, 0, 0, 0, 136, 27]
def setDevice2(state, ser):
    if state == True:
        ser.write(relay2_ON)
    else:
        ser.write(relay2_OFF)

def listening():
    r = sr.Recognizer() 
    
    with sr.Microphone() as mic:
        r.adjust_for_ambient_noise(mic)
        audio = r.listen(mic)
    try:
        return r.recognize_google(audio, language="vi")
    except sr.UnknownValueError or sr.RequestError:
        return None

def getaudiodevices():
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        print(p.get_device_info_by_index(i).get('name'))   

def text_to_speech_2():
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    for voice in voices:
        engine.setProperty('voice', voice.id)
        engine.say('Xin chào')
    engine.runAndWait()

