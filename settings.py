import json

with open("settings.json", "r") as file:
    settings = json.load(file)

print(settings)