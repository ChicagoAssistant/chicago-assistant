<!-- Meta: Wrong requests -->
* fix_pothole
  - ask_location
* wrong_request
  - utter_sorry
  - bug_report_conversation_log
  - restart

* fix_streetlight
  - ask_location
* wrong_request
  - utter_sorry
  - bug_report_conversation_log
  - restart

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

## Fix pothole: Misunderstood by bot
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
    - utter_no_problem
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

## Fix pothole: Exact address unknown
* fix_pothole
  - ask_location
* dont_know
  - utter_no_problem
  - ask_general_location
* give_approximate_location
  - offer_address_suggestions
* give_location
  - ask_location_details
* give_location_details
  - confirm_request
* affirm
  - utter_thank_you
  - submit_request