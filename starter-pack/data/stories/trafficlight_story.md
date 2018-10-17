<!-- All traffic lights are out -->
## all_lights_out
* traffic_light{"REQUEST_TYPE": "traffic_light"}
    - slot{"REQUEST_TYPE": "traffic_light"}
    - ask_location
* location{"LOCATION": "123 Main St"}
    - confirm_location
    - ask_problem
* signal_all_out
    - utter_confirmation
* confirm
    - utter_submission
    - utter_goodbye

<!-- Some traffic lights are out -->
## some_lights_out
* traffic_light
    - ask_location
* location
    - confirm_location
    - ask_problem
* signal_some_out
    - utter_confirmation
* confirm
    - utter_submission
    - utter_goodbye

<!-- Traffic lights are flashing -->
## lights_flashing
* traffic_light
    - ask_problem
* signal_flashing
    - ask_flashing_light_color
* light_color
    - ask_location
* location
    - confirm_location
* confirm
    - utter_confirmation
* confirm
    - utter_submission
    - utter_goodbye