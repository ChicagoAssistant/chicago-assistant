<!-- Request: Fixing a Pothole -->
## Fix pothole: Ideal
* fix_pothole
    - ask_location
* give_pothole_location
    - ask_location_details
* give_location_details
    - confirm_request
* affirm
    - utter_thank_you
    - submit_request

## Fix pothole: Misunderstood
* fix_pothole
    - ask_location
* give_pothole_location
    - ask_location_details
* give_location_details
    - confirm_request
* deny
    - restart

## Fix pothole: No location details
* fix_pothole
    - ask_location
* give_location
    - ask_location_details
* dont_know
    - confirm_request
* affirmative
    - utter_thank_you
    - submit_request

## Fix pothole: Address not found
* fix_pothole
    - ask_location
* give_location
    - utter_address_not_found
    - offer_address_suggestions
* give_location
    - ask_location_details
* give_location_details
    - confirm_request
* affirm
    - utter_thank_you
    - submit_request