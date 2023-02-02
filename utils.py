import json


def print_response(res, indent=2):
    print(json.dumps(res.json(), indent=indent))





def read_config(path):
    return json.load(open(path))