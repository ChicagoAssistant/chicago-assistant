## Team Name: Civic Chifecta
### Project: Chicago 311 Virtual Agent

Our solution can be accessed at http://chicago-311-agent.herokuapp.com/

Our web application is hosted on Heroku via the 'production' branch of our GitHub repository. The python files that are used live by the solution are:
    
    - server.py: holds main functions used to direct flow of conversation with DialogFlow and submitting requests to Chicago's Open311. Also renders the webpage where our solution is hosted.

    - util.py: holds helper functions used in server.py

    - chi311_import.py: holds code used to create initial tables and manage daily table updates

    - queries.py: holds queries that are used to query the average historical time for request fulfilment

Code that was used to gather 311 data from other cities can be found in the 'data_collection' folder in our repository.

### Description of Code Structure: 
- Our code is used each time DialogFlow sends a webhook request to our web application. For an example of the data that is passed to our web application, see an example here: https://github.com/civicchifecta/311-agent/blob/master/example_dialogflow_request.json 
- Our 'server.py' file handles the bulk of our functionality with support from 'util.py' and 'queries.py'. When a user messages our virtual agent, DialogFlow handles the conversation independently except for in the following key situations:
    1. When a user gives an address, the address is passed to our python web application via webhook to process and verify that it is an address. If not an address or if multiple addressess are matched, then our web application passes back up to three recommended addresses to select from.
    2. When all pertinent request information has been collected from the user, the information is sent to our web application via webhook and our code parses the information to structure and post the reqeust to the Open311 system. Also, this is the point where our web application will query our databases to get the average response times in addition to recording the user interaction in our databases.
    3. There are several points in the conversation that our web application is used to direct the flow of conversation - this can be seen in the "makeWebhookRequest" function. The different actions shown in the followupEvent function correspond to an "Intent" in DialogFlow triggered by the followup event (see https://dialogflow.com/docs/events for more info).

NOTE: The flow of conversation, natural language processing, and integration with Skype are all completed within the DialogFlow platform. Areas of interest within DialogFlow are the "Intents" section and the "Entities". You can access DialogFlow at http://www.dialogflow.com


### Team member contributions:

Loren

Darshan

Vidal was responsible for implementing the flow of dialogue into DialogFlow and writing the code that integrated DialogFlow with our web application (makeWebhookResult and all functions and helper functions used by makeWebhookResult). In DialogFlow, you can see each of the "Intents" that trigger each part of the conversation. Similarly, you can see the "Entities" we created in order to map a users response to the data we needed to push to the Open311 API (example: user says, 'hole in the street', the Entity returns, 'pothole'). Vidal also wrote the code which posts the service request to Chicago's Open311 system (see API documentation here: http://dev.cityofchicago.org/docs/open311/).


## Instructions for Trying the Solution and Verifying Successful Trial

1. Go to http://chicago-311-agent.herokuapp.com/
2. Initiate conversation with a greeting of your choice.
3. Indicate in your own words the type of request you'd like to submit, or use one of the buttons.
4. Opt to give a name or skip.
5. Provide an address, cross street, or establishment name. If more than one match is returned by Google Maps Autocomplete, the top three matches will be returned to the messaging interface for the user to select from.
6. A service-type-specific question will be asked by the virtual agent (example: for potholes, the virtual agent asks if the pothole is in the intersection, curb lane, bike lane, crosswalk, or traffic lane). If the same question is asked again, it means that the virtual agent was unable to match your response to any of the five options listed above.
7. Provide a description, any description text would do.
8. The agent will ask if you'd like to be notified - here you have the option of providing a phone and email. To skip, press "No, thank you." or reject in a negatory experession of your choice.
9. At this point, our solution will structure and push the request to Chicago's Open311 system and will query our databases to get an average time of completion for the given service request type.
10. Successful completion of these two tasks are indicated by "Your request has been submitted successfully!" OR "Your request is a duplicate in our system!" and "Requests for _ in the _ area are typically serviced within _ days at this time of year.", respectively.
11. The virtual agent will ask for feedback using the buttons, and will ask for any additional feedback as an open field. NOTE: feedback is currently not being collected in our databases.
12. Conversation ends with the agent providing option to go back to the main menu.

### Verify that Request Posted to Chicago's Open311 Systems
Pull back requests using the following instructions:
1. Open up an ipython instance
2. Run the following:

    ```
    import requests
    url = 'http://test311api.cityofchicago.org/open311/v2/requests.json'
    requests.get(url).json()
    ```

3. The code above returns a list of dictionaries holding previously submitted requests. You should see your request at the top of the results.

### Verify that User Interactions are Logged
To verify that the user interaction was logged in our database, you can connect to our database tables using the tool of your choice. We recommend pgAdmin4. You can connect to our database by using the credentials provided in our credentials.txt file in the folder we shared with you.
1. Connect to the database using provided credentials.
2. View the 'dialogflow_transactions' table to see stored user interactions.

### See Historical Request Data
To see historical request data that we query when calculating average response times, you can connect to our database and see the tables in the public schema. Again, credentials for connecting to our database can be found in the 'credentials.txt' we provided via the folder we shared with you.

## Data Sources

**Historical Chicago 311 Request Data:** We used data from Chicago's Open Data Portal, specifically pothole, rodent baiting, and street light requests from the last 4 years.

**Training Phrase Data From Multiple Cities:** In order to train our agent, we explored and used raw text data from Cincinnati, Baton Rouge, Gainesville, Kansas City, New Orleans, and Chicago.