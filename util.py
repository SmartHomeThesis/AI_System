import os
import time
import wave
import playsound

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
    channels = 1
    sample_rate = 44100
    record_seconds = 3
    micro_index =1 
    p = pyaudio.PyAudio()
    # open stream object as input & output
    stream = p.open(format=FORMAT, channels=channels, rate=sample_rate, input=True, frames_per_buffer=chunk, input_device_index=micro_index)
    frames = []

    print("Listening...")
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
    except sr.UnknownValueError:
        print("Could not understand audio")
        return None
    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))
        return None

def text_to_speech(msg):
    audio = gTTS(msg, lang="vi")
    audio.save("audio.mp3")
    playsound.playsound("audio.mp3")
    os.remove("audio.mp3")

