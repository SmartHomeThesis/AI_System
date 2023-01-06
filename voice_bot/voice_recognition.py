import os
import wave
import pyaudio
import requests
import playsound
import speech_recognition as sr   
from gtts import gTTS
# from .speaker_verification import test_model


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
                    output=True,
                    frames_per_buffer=chunk)
    frames = []
    for i in range(int(sample_rate / chunk * record_seconds)):
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


def text_to_speech(message):
    myobj = gTTS(message, lang="vi")
    myobj.save("audio.mp3")
    print("Converts text to speech")
    playsound.playsound("audio.mp3")
    print("Removes audio.mp3 file")
    os.remove("audio.mp3")


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
                print("Something is wrong. Please try again!!!")    
        
        if len(user_message) == 0:
            continue
        
        # Speaker verification 
        # print(test_model("user.wav") + ": {}".format(user_message))
        print(user_message)

        os.remove("user.wav")
        print("*******************************************************")

        r = requests.post('http://localhost:5002/webhooks/rest/webhook', json={"message": user_message})

        for i in r.json():
            if "False" in i["text"]:
                bot_message = i['text'][:i['text'].index(".")]
            else:
                bot_message = i["text"]
                text_to_speech(bot_message) 
                   
            print("Bot: " + f"{bot_message}")
