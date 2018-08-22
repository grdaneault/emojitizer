import json
from PIL import Image, ImageStat
from rtree import index
import os

with open("custom_emoji/emoji.json") as config_file:
    config = json.load(config_file)

properties = index.Property()
properties.dimension = 3
index = index.Index("custom_emoji/emoji_rgb", properties=properties)


def convert_image(img, display_size=16, write_file=False, write_screen=True, max_cols=48, max_rows=32, min_chunk_size=16):
    im = Image.open(img).convert("RGB")

    sizes = [im.width // max_cols, im.height // max_rows, min_chunk_size]
    chunk_size = max(sizes)

    html = ""
    messages = []
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
        if not messages:
            messages.append(slack)
        elif len(messages[-1]) + len(slack) < 4000:
            messages[-1] += slack
        else:
            messages.append(slack)
        slack = ""
    file, ext = os.path.splitext(img)

    if write_screen:
        for msg in messages:
            print(msg)
            print("-" * 80)

    if write_file:
        with open(file + ".html", "w") as out:
            out.write(html)

    return messages


if __name__ == '__main__':
    convert_image("samples/poop.png", chunk_size=16, display_size=32, write_file=True, write_screen=True)


