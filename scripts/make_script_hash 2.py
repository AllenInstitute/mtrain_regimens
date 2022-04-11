import requests
from hashlib import md5


def make_script_hash(uri):
    r = requests.get(uri)
    return md5(r.text.encode("latin1")).hexdigest


if __name__ == "__main__":
    import sys

    print(make_script_hash(sys.argv[1]))