from rasa_nlu.model import Interpreter
import json

interpreter = Interpreter.load("./models/current/nlu")
message = "there's a problem with a traffic light"
result = interpreter.parse(message)
print(json.dumps(result, indent=2))