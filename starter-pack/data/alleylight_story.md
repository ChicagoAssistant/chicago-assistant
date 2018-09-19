## action:utter_greet

- Hello, how can I help out today?

## intent:greet

- hey
- hello
- hi
- Hi!
- hello there
- good morning
- good evening
- moin
- hey there
- let's go
- hey dude
- goodmorning
- goodevening
- good afternoon

## intent:alleylight

- there's a [street light] out (StreetLight)
- there's a [streetlight] out (StreetLight)
- there's a [light pole] out (StreetLight)
- there's a [lamppost] out (StreetLight)
- there's a [street lamp] out (StreetLight)
- there's a [light standard] out (StreetLight)
- there's a [lamp standard] out (StreetLight)
- there's a [light] out (StreetLight; ambiguous; need to cross-reference with AlleyLight)
- I found a [street light] that's broken (StreetLight)
- broken [street light](StreetLight)
- broken [streetlight](StreetLight)
- broken [light pole](StreetLight)
- broken [lamppost](StreetLight)
- broken [street lamp](StreetLight)
- broken [light standard](StreetLight)
- broken [lamp standard](StreetLight)
- There's a [streetlight] out at [street](Location)

## action:utter_description

- Is the light completely out or does it go on and off?

## action:utter_photo_upload

- Would you like to upload a photo of the street light?

## action:utter_coordinates

- Where is the street light located?

## intent:coordinates

- at [street] and [street]
- 1234 Somewhere Ave
- 1234 Somewhere Ave, 60601
- 60601

## action:utter_order

- Would you like to submit a 311 order request for the street light?

## action:utter_confirmation

- I have that the street light is located in the (Location) at (Coordinates). Is that right?

## action:utter_updates

- Would you like to opt in to text updates about this street light?

## action:utter_updates_confirmed

- Great! What number should we send text updates to?

## action:utter_updates_number_incomplete

- Sorry; I need a 10-digit phone number to send updates. Can you give me your 10-digit phone number?

## action:utter_updates_number

- Thanks!

## action:utter_submission

- We have submitted your 311 request; thanks! Is there anything else I can help out with?

## action:utter_goodbye

- Thank you for using Chi Virtual Assistant. Goodbye!

## intent:goodbye

- cu
- good by
- cee you later
- good night
- good afternoon
- bye
- goodbye
- have a nice day
- see you around
- bye bye
- see you later

## intent:confirm

- yes
- indeed
- of course
- yup
- yeah
- that sounds good
- correct

## intent:deny

- no
- nope
- that's not it
- never
- I don't think so
- don't like that
- no way
- no thank you
- no thanks
- no I don't want to

## intent:updates_number

- (PhoneNumber; 10 digits)

## intent:updates_number_incomplete

- (PhoneNumber; < 10 digits)
