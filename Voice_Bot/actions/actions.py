from typing import Any, Text, Dict, List, Union

import arrow
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

city_db = {
    'London': 'Europe/London',
    'Việt Nam': 'Asia/Hanoi'
}

command_db = {
    'tắt': 0,
    'mở': 1,
    'bật': 2
}

device_db = {
    'đèn': 0,
    'quạt': 1  
}


class ActionTellTime(Action):

    def name(self) -> Text:
        return "action_tell_time"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        current_place = next(tracker.get_latest_entity_values("place"), None)
        utc = arrow.utcnow()
        
        if not current_place:
            msg = f"Bây giờ là {utc.to(city_db['Việt Nam']).format('HH:mm')} phút."
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

    # def helper(device, command):
    #     if device == "quạt":
    #         if command == "tắt":
    #             setDevice1(False)
    #         else:
    #             setDevice1(True)    
    #     else:
    #         if command == "tắt":
    #             setDevice2(False)
    #         else:
    #             setDevice2(True)         
    
    def run(self, dispatcher: CollectingDispatcher, 
            tracker: Tracker, 
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        current_command = next(tracker.get_latest_entity_values("command"), None)
        current_device = next(tracker.get_latest_entity_values("device"), None)
        
        if not current_device:
            msg = f"Bạn muốn thao tác với thiết bị gì?"
            dispatcher.utter_message(text=msg)
            return []
                
        if current_command != None:        
            msg = f"{current_device} đã được {current_command}."
            dispatcher.utter_message(text=msg)
            return [] 
        else:
            msg = f"Bạn muốn bật hay tắt {current_device}?"
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

