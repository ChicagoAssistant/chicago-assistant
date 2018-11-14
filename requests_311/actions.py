from rasa_core_sdk.forms import FormAction, REQUESTED_SLOT
from rasa_core_sdk.events import SlotSet


class PotholeRequestForm(FormAction):
    """Example of a custom form action"""
    def name(self):
        # type: () -> Text
        """Unique identifier of the form"""

        return "pothole_request_form"

    @staticmethod
    def required_slots(tracker):
        # type: () -> List[Text]
        """A list of required slots that the form has to fill"""

        return ["location", "description", "pothole_location"]

    def slot_mappings(self):
        """A dictionary to map required slots to
            - an extracted entity
            - intent: value pairs
            - a whole message
            or a list of them, where a first match will be picked"""

        return {"location": self.from_text(intent="pothole"),
                "description": self.from_text(intent="pothole_description"),
                "pothole_location": self.from_entity(entity="",
                                                     intent="") }

    def submit(self, dispatcher, tracker, domain):
        # type: (CollectingDispatcher, Tracker, Dict[Text, Any]) -> List[Dict]
        """Define what the form has to do
           after all required slots are filled"""

        # utter submit template
        dispatcher.utter_template('utter_submit', tracker)
        return []
