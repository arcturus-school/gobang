import json


def json_to_byte(json_):
    return json.dumps(json_).encode('gb2312')


def byte_to_json(byte_):
    return json.loads(byte_.decode('gb2312'))
