from typing import Any, Text, Dict, List

import arrow
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


city_db = {
    'việt nam': 'Asia/Hanoi',
    'london': 'Europe/London',
    'new york': 'US/Central'
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
            # helper(current_device, current_command)
            return [] 
        else:
            msg = f"Bạn muốn bật hay tắt {device}?"
            dispatcher.utter_message(text={"msg": msg, "is_sound": False})
            return [] 
  
class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_your_num"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(tracker.get_slot('num'))
        return []

