import json
import glob
import requests


def download_file(url, name):
    resp = requests.get(url, allow_redirects=True)
    name = "img/{}.png".format(name)
    open(name, 'wb').write(resp.content)


for config in glob.glob("*.json"):
    config = json.load(open(config))
    for emoji in config:
        emoji['name'] = emoji['name'].strip(":")
        print("{name}: {url}".format(**emoji))
        download_file(**emoji)



