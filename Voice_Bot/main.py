# rasa run -m models --endpoints endpoints.yml --port 5002 --credentials credentials.yml

import os
import requests
import playsound
import speech_recognition as sr   
from gtts import gTTS
from pydub import AudioSegment
from Speaker_Id.main import test_model

cnt = 0
bot_message = ""
user_message = ""

    
# Start the conversation
print("*******************************************************")
bot_message = "Xin chào, bạn khỏe không?"
print("Bot says: " + f"{bot_message}")

# Text-to-speech
myobj = gTTS(bot_message, lang="vi")
myobj.save("bot.mp3")
playsound.playsound("bot.mp3")
os.remove("bot.mp3")


while bot_message != "Bye":
    r = sr.Recognizer()
    r.energy_threshold = 300
    with sr.Microphone() as source:  
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source, phrase_time_limit = 5)  

        try:
            user_message = r.recognize_google(audio, language="vi-VI") 

            # Text-to-speech
            myobj = gTTS(user_message, lang="vi") 
            myobj.save("user.mp3")
            sound = AudioSegment.from_mp3("user.mp3")
            sound.export("user.wav", format="wav")

            print(test_model("user.wav") + " said: {} ".format(user_message))

        except:
            if cnt < 1:
                cnt = cnt + 1
                print("Bot says: Xin chào, bạn cần giúp gì nhỉ?")
                

    if len(user_message) == 0:
        continue

    print("*******************************************************")

    r = requests.post('http://localhost:5002/webhooks/rest/webhook', json={"message": user_message})

    for i in r.json():
        bot_message = i['text']
        print("Bot says: " + f"{bot_message}")
    
    myobj = gTTS(bot_message, lang="vi")
    myobj.save("bot.mp3")
    playsound.playsound("bot.mp3")
    
    
    os.remove("bot.mp3")
    os.remove("user.mp3")
    os.remove("user.wav")