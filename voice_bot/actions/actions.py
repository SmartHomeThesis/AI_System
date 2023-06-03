from typing import Any, Dict, List, Text

import arrow
import requests
from rasa_sdk import Action
from rasa_sdk.events import SlotSet


class ActionGetWeather(Action):
    """ Return today's weather forecast"""
    def name(self):
        return "action_tell_weather"

    def run(self, dispatcher, tracker, domain):
        city = tracker.get_slot('location')
        api_token = "ad176833d289a46575e361b22f782cb6"
        url = "https://api.openweathermap.org/data/2.5/weather"
        payload = {"q": city, "appid": api_token, "units": "metric", "lang": "vi"}
        response = requests.get(url, params=payload)

        if response.ok:
            description = response.json()["weather"][0]["description"]
            temp = round(response.json()["main"]["temp"])
            city = response.json()["name"]
            msg = f"Thời tiết hiện tại ở thành phố {city} là {temp} độ C. Hôm nay {description}"
        else:
            msg = "Xin lỗi, tôi không thể tìm thấy thành phố đó"
        dispatcher.utter_message(msg)
        return [SlotSet("location", None)]


class ActionTellTime(Action):

    def name(self) -> Text:
        return "action_tell_time"

    # def run(self, dispatcher, tracker, domain) -> List[Dict[Text, Any]]:
    #     current_place = next(tracker.get_latest_entity_values("place"), None)
    #     utc = arrow.utcnow()
    #
    #     if not current_place:
    #         msg = f"Bây giờ là {utc.to('Asia/Hanoi').format('HH:mm')} phút."
    #         dispatcher.utter_message(text=msg)
    #         return []
    #
    #
    #
    #
    #     tz_string = city_db.get(current_place, None)
    #     if not tz_string:
    #         msg = f"Tôi không tìm thấy {current_place}. Bạn có chắc về sự tồn tại của nơi này không?"
    #         dispatcher.utter_message(text=msg)
    #         return []
    #
    #     msg = f"Bây giờ là {utc.to(result).format('HH:mm')} ở {current_place}."
    #     dispatcher.utter_message(text=msg)
    #
    #     return []

class ActionControlDevice(Action):

    def name(self) -> Text:
        return "action_control_device"

    def run(self, dispatcher, tracker, domain) -> List[Dict[Text, Any]]:

        command = next(tracker.get_latest_entity_values("command"), None)
        device = next(tracker.get_latest_entity_values("device"), None)
        
        if not device:
            msg = f"Bạn muốn thao tác với thiết bị gì?"
            dispatcher.utter_message(text=msg)
            return []
                
        if command != None:        
            msg = f"{device} đã được {command}"
            dispatcher.utter_message(text=msg)
            return [] 
        else:
            msg = f"Bạn muốn thực hiện hành động gì với {device}?"
            dispatcher.utter_message(text=msg)
            return [] 
  
class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_your_num"

    def run(self, dispatcher, tracker, domain) -> List[Dict[Text, Any]]:
        print(tracker.get_slot('num'))
        return []

