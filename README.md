## Chicago Assistant

The Chicago Assistant is a text and voice interface for requesting city services and making inquires about city services. Functionalities we are currently exploring include:
 - Submit 311 Service Requests
 - Get transit arrival times and station accessibility information
 - Request information about common city services such as getting a vehicle city sticker, school closures, street cleaning schedules, etc.
 - Contacting your alderman
 - Got an idea? [Share it with us!](google.com)

The text and voice interface could be integrated with popular messaging platforms like Facebook Messenger and popular voice interfaces like Amazon Alexa and Google Assistant.

The project aims to improve ease of accessibility to city services and information about city services by creating a text and voice channel to compliment existing web and telephone (311) channels.

# Starter Pack for Rasa Stack

This starter pack helps you build a bot faster with [Rasa Stack](http://rasa.com/products/rasa-stack/). Apart from a basic file and folder structure, it gives you some initial training data. Clone this repo and start building your bot.

For more information on the Rasa Stack, please visit the docs here:
- [Rasa Core](https://core.rasa.com/)
- [Rasa NLU](https://nlu.rasa.com/)

## Setup

To install the necessary requirements, run:

```
pip install -r requirements.txt
```

## Usage

To train the NLU model, run ``make train-nlu``

To train the Core model, run ``make train-core``

To run the bot on the command line run ``make cmdline``

## What now?

To continue developing your bot, you can start by adding some NLU data for intents/entities relevant to your use case. These then need to be added to your domain file. From there you can add more utterances for the bot, or custom actions you've written in `actions.py` and then write stories using these.

### Join Us At Chi Hack Night
**Slack Channel** #chivirtualassistant
