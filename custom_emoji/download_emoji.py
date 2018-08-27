import json
import glob
import requests
import os
from slackclient import SlackClient


def download_file(url, name):
    file_type = url.split(".")[-1]
    file_name = "img/{}.{}".format(name, file_type)
    if not os.path.exists(file_name):
        print("Downloading {} as {}... ".format(name, file_name), end="")
        resp = requests.get(url, allow_redirects=True)
        open(file_name, 'wb').write(resp.content)
        print("done.")
    else:
        print("Skipping {} as {}...".format(name, file_name))


client = SlackClient(os.environ.get('SLACK_TOKEN_2'))

emoji = client.api_call("emoji.list")

for name in emoji['emoji']:
    url = emoji['emoji'][name]
    if url.startswith("alias"):
        continue
    else:
        download_file(url, name)
