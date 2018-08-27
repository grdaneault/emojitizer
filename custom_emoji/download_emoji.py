import json
import glob
import requests


def download_file(url, name):
    resp = requests.get(url, allow_redirects=True)
    file_type = url.split(".")[-1]
    name = "img/{}.{}".format(name, file_type)
    open(name, 'wb').write(resp.content)


for config in glob.glob("*.json"):
    if config != "emoji.json":
        config = json.load(open(config))
        for emoji in config:
            emoji['name'] = emoji['name'].strip(":")
            print("{name}: {url}".format(**emoji))
            download_file(**emoji)
