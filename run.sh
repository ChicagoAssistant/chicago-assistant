#!bin/bash

python3 -m rasa_nlu.train -c nlu_config.yml --data data/nlu_data.md -o models --fixed_model_name nlu --project current --verbose

# from rasa_nlu.training_data import load_data
# from rasa_nlu.config import RasaNLUModelConfig
# from rasa_nlu.model import Trainer
# from rasa_nlu import config
#
# training_data = load_data("data/nlu_data.md")
#
# trainer = Trainer(config.load("nlu_config.yml"))
#
# interpreter = trainer.train(training_data)
#
# model_directory = trainer.persist("./models/nlu", fixed_model_name="current")


python3 -m rasa_core.train -d domain.yml -s data/stories.md -o models/current/dialogue --epochs 200
#
# from rasa_core.policies import FallbackPolicy, KerasPolicy, MemoizationPolicy
# from rasa_core.agent import Agent
#
# agent = Agent("domain.yml", policies=[MemoizationPolicy(), KerasPolicy()])
#
# training_data = agent.load_data("data/stories.md")
#
# agent.train(
#     training_data,
#     validation_split = 0.0,
#     epochs = 300)
#
# agent.persist("models/dialogue")


python3 -m rasa_core.run -d models/current/dialogue -u models/current/nlu

# print("Your bot is ready to talk: Type your messages here or send 'stop'")
# while True:
#     a = input()
#     if a == 'stop':
#         break
#     responses = agent.handle_message(a)
#     for response in responses:
#         print(response['text'])
