import json

import math
from PIL import Image, ImageStat
from rtree import index
import os
import random

from transparency_helper import rgbtize

with open("custom_emoji/emoji.json") as config_file:
    config = json.load(config_file)

properties = index.Property()
properties.dimension = 3

index_color = index.Index("full_emoji", properties=properties)
index_nocolor = index.Index("current_emoji", properties=properties)


def convert_image(img, display_size=32, write_file=False, write_screen=True, write_img=False, max_width=None, max_cols=48, max_height=None, max_rows=32, min_chunk_size=16, include_tones=False, include_colors=True, outdir="samples/converted"):
    print("Converting Image " + img)
    im = rgbtize(Image.open(img))

    print("image is {}x{}".format(im.width, im.height))

    if max_width is not None and max_height is not None:
        horiz_chunks = max_width // display_size
        vert_chunks = max_height // display_size
    else:
        horiz_chunks = max_cols
        vert_chunks = max_rows

    chunk_size = max([im.width / horiz_chunks, im.height/vert_chunks])
    chunk_size = math.ceil(chunk_size)

    print("chose chunk size of {}px\n\n".format(chunk_size))
    html = ""
    messages = []
    slack = ""
    out_img = Image.new("RGB", ((im.width // chunk_size) * display_size, (im.height // chunk_size) * display_size), "white")

    for y in range(im.height // chunk_size):
        for x in range(im.width // chunk_size):
            piece = im.crop(box=(x * chunk_size, y * chunk_size, (x + 1) * chunk_size, (y + 1) * chunk_size))
            stats = ImageStat.Stat(piece)
            coords = stats.mean + stats.mean
            if include_colors:
                nearest = index_color.nearest(coords, num_results=3, objects=True)
            else:
                nearest = index_nocolor.nearest(coords, num_results=3, objects=True)

            def include_choice(choice):
                if choice.object is None:
                    return False
                if not include_tones and choice.object['name'].startswith("skin-tone-"):
                    return False
                return True

            emoji = random.choice(list(filter(include_choice, nearest))).object
            html += '<img src="../{0}" width="{1}" height="{1}" />'.format(emoji['path'], display_size)
            slack += ":{}:".format(emoji['name'])

            if write_img:
                emoji_im = rgbtize(Image.open(emoji['path'])).resize((display_size, display_size))
                out_img.paste(emoji_im, (x * display_size, y * display_size, (x + 1) * display_size, (y + 1) * display_size))

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

    name = os.path.basename(file)
    if write_file:
        with open(os.path.join(outdir, file) + ".html", "w") as out:
            out.write(html)


    if write_img:
        out_img.save(os.path.join(outdir, "{}.png".format(name)))

    return messages


if __name__ == '__main__':
    for img in os.listdir("samples"):
        if img.endswith("html") or img == "converted":
            continue

        file, ext = os.path.splitext(img)
        if os.path.exists("samples/{}.html".format(file)):
            print("already have {}".format(img))
            continue

        convert_image("samples/" + img, write_file=True, write_screen=False, write_img=True, max_width=1920, max_height=1080, display_size=8)


