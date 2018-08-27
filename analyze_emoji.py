import json
import os

from PIL import Image, ImageStat
from rtree import index
from transparency_helper import rgbtize
data = {}


def try_delete(name):
    try:
        os.remove(name)
    except:
        pass


try_delete("full_emoji.dat")
try_delete("full_emoji.idx")
try_delete("current_emoji.dat")
try_delete("current_emoji.dat")

properties = index.Property()
properties.dimension = 3
idx = index.Index('full_emoji', properties=properties)
idx_nocolor = index.Index('current_emoji', properties=properties)

rmin = gmin = bmin = amin = 0
rmax = gmax = bmax = amax = 255


idx.insert(0, (rmin, gmin, bmin, rmax, gmax, bmax))
bucket_size = 5


def analyze_image(emoji, name):
    im = Image.open(emoji)
    if emoji.endswith(".gif") and im.is_animated:
        print("{} is animated".format(emoji))
        return

    rgba = rgbtize(im)
    stats = ImageStat.Stat(rgba)
    name = name.split(".")[0]
    median = stats.median
    mean = stats.mean

    record = {
        "path": emoji,
        "name": name,
        "median": median,
        "mean": mean,
        "index": len(data) + 1
    }
    idx.insert(len(data) + 1, mean + mean, obj=record)

    if not name.startswith("c_"):
        idx_nocolor.insert(len(data) + 1, mean + mean, obj=record)

    data[name] = record

def load_custom_emoji():
    for emoji in os.listdir("custom_emoji/img"):
        analyze_image("custom_emoji/img/" + emoji, emoji)
    for emoji in os.listdir("custom_emoji/new"):
        analyze_image("custom_emoji/new/" + emoji, emoji)

def load_google_emoji():
    google = json.load(open("google/emoji_pretty.json"))
    has_google = [e for e in google if e["has_img_google"] and e["short_names"]]
    for emoji in has_google:
        analyze_image("google/img/" + emoji["image"], emoji["short_names"][0])


load_custom_emoji()
load_google_emoji()

with open("emoji.json", "w") as out:
    json.dump(data, out, indent=2)
