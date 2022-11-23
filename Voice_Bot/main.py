import os
import requests
import playsound
import speech_recognition as sr   
from gtts import gTTS

cnt = 0
bot_message = ""
user_message = ""

    
# Start the conversation
print("Bot says: ", end="")
bot_message = "Xin chào, bạn khỏe không?"
print(f"{bot_message}")

myobj = gTTS(bot_message, lang="vi")
myobj.save("conversation.mp3")
# Playing the converted file
playsound.playsound("conversation.mp3")
os.remove("conversation.mp3")


while bot_message != "Bye":
    user_message = ""

    r = sr.Recognizer()  
    with sr.Microphone() as source:  
        r.adjust_for_ambient_noise(source)

        audio = r.listen(source, phrase_time_limit = 5)  
        try:
            user_message = r.recognize_google(audio, language="vi-VI")  
            print("You said: {}".format(user_message))
        except:
            cnt = cnt + 1
            if cnt < 3:
                print("Bot says: Xin lỗi, tôi không nghe được bạn nói")
                myobj = gTTS("Xin lỗi, tôi không nghe được bạn nói", lang="vi")
                myobj.save("conversation.mp3")
                # Playing the converted file
                playsound.playsound("conversation.mp3")
                os.remove("conversation.mp3")

    if len(user_message) == 0:
        continue

    print("******************************************")

    r = requests.post('http://localhost:5002/webhooks/rest/webhook', json={"message": user_message})

    print("Bot says: ", end="")
    for i in r.json():
        bot_message = i['text']
        print(f"{bot_message}")
    
    myobj = gTTS(bot_message, lang="vi")
    myobj.save("conversation.mp3")
    # Playing the converted file
    playsound.playsound("conversation.mp3")
    os.remove("conversation.mp3")