<!-- All traffic lights are out -->
## all_lights_out
* traffic_light{"request": "traffic_light"}
    - ask_coordinates
* coordinates
    - confirm_coordinates
    - ask_problem
* signal_all_out
    - utter_confirmation
* confirm
    - utter_submission
    - utter_goodbye

<!-- Some traffic lights are out -->
## some_lights_out
* traffic_light
    - ask_coordinates
* coordinates
    - confirm_coordinates
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
    - ask_coordinates
* coordinates
    - confirm_coordinates
* confirm
    - utter_confirmation
* confirm
    - utter_submission
    - utter_goodbye