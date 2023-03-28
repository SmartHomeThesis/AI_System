from typing import Any, Text, Dict, List

import arrow
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import requests


city_db = {
    'việt nam': 'Asia/Hanoi',
    'london': 'Europe/London',
    'new york': 'US/Central'
}


class ActionGetWeather(Action):
    """ Return today's weather forecast"""
    def name(self):
        return "action_get_weather"

    def run(self, dispatcher, tracker, domain):
        city = tracker.get_slot('location')
        api_token = "ad176833d289a46575e361b22f782cb6"
        url = "https://api.openweathermap.org/data/2.5/weather"
        payload = {"q": city, "appid": api_token, "units": "metric", "lang": "en"}
        response = requests.get(url, params=payload)
        if response.ok:
            description = response.json()["weather"][0]["description"]
            temp = round(response.json()["main"]["temp"])
            city = response.json()["name"]
            msg = f"The current temperature in {city} is {temp} degree Celsius. Today's forecast is {description}"
        else:
            msg = "I'm sorry, an error with the requested city as occured."
        dispatcher.utter_message(msg)
        return [SlotSet("location", None)]


class ActionTellTime(Action):

    def name(self) -> Text:
        return "action_tell_time"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        current_place = next(tracker.get_latest_entity_values("place"), None)
        utc = arrow.utcnow()
        
        if not current_place:
            msg = f"Bây giờ là {utc.to(city_db['việt nam']).format('HH:mm')} phút."
            dispatcher.utter_message(text=msg)
            return []
        
        tz_string = city_db.get(current_place, None)
        if not tz_string:
            msg = f"Tôi không tìm thấy {current_place}. Bạn có chắc về sự tồn tại của nơi này không?"
            dispatcher.utter_message(text=msg)
            return []
                
        msg = f"Bây giờ là {utc.to(city_db[current_place]).format('HH:mm')} ở {current_place}."
        dispatcher.utter_message(text=msg)
        
        return []

class ActionControlDevice(Action):

    def name(self) -> Text:
        return "action_control_device"

    def run(self, dispatcher: CollectingDispatcher, 
            tracker: Tracker, 
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        command = next(tracker.get_latest_entity_values("command"), None)
        device = next(tracker.get_latest_entity_values("device"), None)
        
        if not device:
            msg = f"Bạn muốn thao tác với thiết bị gì?"
            dispatcher.utter_message(text=msg)
            return []
                
        if command != None:        
            msg = f"{device} đã được {command}. False"
            dispatcher.utter_message(text=msg)
            return [] 
        else:
            msg = f"Bạn muốn bật hay tắt {device}?"
            dispatcher.utter_message(text=msg)
            return [] 
  
class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_your_num"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(tracker.get_slot('num'))
        return []

