import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = os.path.join(BASE_DIR, "data")

FILES = {
    "users": "users.json",
    "leave_requests": "leave_requests.json"
}


def initialize_storage():
    os.makedirs(DATA_FOLDER, exist_ok=True)

    for filename in FILES.values():
        path = os.path.join(DATA_FOLDER, filename)

        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as file:
                json.dump([], file, indent=4)


def read_json(filename):
    path = os.path.join(DATA_FOLDER, filename)

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def write_json(filename, data):
    path = os.path.join(DATA_FOLDER, filename)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)