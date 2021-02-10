import requests
import argparse
import yaml
from hashlib import md5


def get_behavior_script(script_uri):
    r = requests.get(script_uri)
    response_hash = md5(r.text.encode("latin1")).hexdigest()
    return md5(r.text.encode("latin1")).hexdigest()
    return response_hash == expected_script_hash


parser = argparse.ArgumentParser()
parser.add_argument("regimen_path")
args = parser.parse_args()

with open(args.regimen_path, "r") as f:
    regimen = yaml.load(f)

actual_hash = get_behavior_script(regimen["_change_detection_script"])

assert actual_hash == regimen["_change_detection_script_md5"], \
    "script should have the hash we expect"
