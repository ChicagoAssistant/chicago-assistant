<!-- Do we need stories for alley light description denial and photo upload denial? -->

## alley_light_out
* greet
    - utter_greet
* alley_light{“REQUEST_TYPE”: “alley_light”}
	- ask_location
* location{“LOCATION”: “123 Main St”}
	- confirm_location
	- ask_alley_light_description
* confirm
	- ask_photo_upload
* confirm
	- utter_confirmation
* confirm 
	- utter_submission_anything_else
* deny
	- utter_goodbye

<!-- alley light description denial -->
## alley_light_out
* greet
    - utter_greet
* alley_light{“REQUEST_TYPE”: “alley_light”}
	- ask_location
* location{“LOCATION”: “123 Main St”}
	- confirm_location
	- ask_alley_light_description
* deny
	- ask_alley_light_photo_upload
* confirm
	- utter_confirmation
* confirm 
	- utter_submission_anything_else
* deny
	- utter_goodbye
