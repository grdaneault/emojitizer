import json
from PIL import Image, ImageStat
from rtree import index
import os

with open("custom_emoji/emoji.json") as config_file:
    config = json.load(config_file)

properties = index.Property()
properties.dimension = 3
index = index.Index("custom_emoji/emoji_rgb", properties=properties)


def convert_image(img, chunk_size=8, display_size=16):
    im = Image.open(img).convert("RGB")
    html = ""
    slack = ""
    for y in range(im.height // chunk_size):
        for x in range(im.width // chunk_size):
            piece = im.crop(box=(x * chunk_size, y * chunk_size, (x + 1) * chunk_size, (y + 1) * chunk_size))
            stats = ImageStat.Stat(piece)
            coords = stats.mean + stats.mean
            nearest = index.nearest(coords, num_results=2, objects=True)
            emoji = next(filter(lambda i: i.object is not None, nearest)).object
            html += '<img src="../custom_emoji/img/{0}" width="{1}" height="{1}" />'.format(emoji['path'], display_size)
            slack += ":{}:".format(emoji['name'])
        html += "<br />"
        slack += "\n"
    file, ext = os.path.splitext(img)
    print(slack)
    with open(file + ".html", "w") as out:
        out.write(html)


convert_image("samples/bliss.jpg", chunk_size=4, display_size=8)



