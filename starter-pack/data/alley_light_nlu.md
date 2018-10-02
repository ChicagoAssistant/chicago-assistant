## action:utter_greet

- Hello, how can I help out today?

## intent:greet

- hey
- hello
- hi
- Hi!
- Howdy
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

- there's an [alley light] out (AlleyLight)
- there's an [alleylight] out (AlleyLight)
- there's a [light] out (ambiguous; need to specify between alley light, light pole, stoplight)
- I found an [alley light] that's broken (AlleyLight)
- broken [alley light](AlleyLight)
- broken [alleylight](AlleyLight)
- broken [light](AlleyLight; ambiguous; need to specify between alley light and street light)
- [Alley light] broke (AlleyLight)
- [Alleylight] broke (AlleyLight)
- [light] broke (AlleyLight; ambiguous)

## action:utter_coordinates

- Where is the alley light located?

## intent:coordinates

- at [street] and [street]
- 1234 Somewhere Ave
- 1234 Somewhere Ave, 60601
- 60601

## action:utter_confirmation

- I have that the street light is located in the (Location) at (Coordinates). Is that right?

## action:utter_description

- Is the light directly behind this address?

## action:utter_photo_upload

- Would you like to upload a photo of the alley light?

## action:utter_order

- Would you like to submit a 311 order request for the alley light?

## action:utter_updates_confirmed

- Great! What number should we send text updates to?

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
