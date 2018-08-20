import glob
import json
import os

from rtree import index

from PIL import Image, ImageStat

data = {}

properties = index.Property()
properties.dimension = 3
idx = index.Index('emoji_rgb', properties=properties)

rmin = gmin = bmin = amin = 0
rmax = gmax = bmax = amax = 255



idx.insert(0, (rmin, gmin, bmin, rmax, gmax, bmax))
bucket_size = 5


def mk_range(r, g, b, a):
    return (r, g, b, a, r, g, b, a)
    # return ((r // bucket_size) * bucket_size,
    #         (g // bucket_size) * bucket_size,
    #         (b // bucket_size) * bucket_size,
    #         (a // bucket_size) * bucket_size,
    #         ((r + bucket_size) // bucket_size) * bucket_size,
    #         ((g + bucket_size) // bucket_size) * bucket_size,
    #         ((b + bucket_size) // bucket_size) * bucket_size,
    #         ((a + bucket_size) // bucket_size) * bucket_size)


os.chdir("img")
i = 1
for emoji in os.listdir("."):
    im = Image.open(emoji)
    if emoji.endswith(".gif") and im.is_animated:
        print("{} is animated".format(emoji))
        continue

    rgba = im.convert("RGB")
    stats = ImageStat.Stat(rgba)
    name = emoji.split(".")[0]
    median = stats.median
    mean = stats.mean

    record = {
        "path": emoji,
        "name": name,
        "median": median,
        "mean": mean,
        "index": i
    }
    idx.insert(i, mean + mean, obj=record)
    i += 1

    data[name] = record


os.chdir("..")
with open("emoji.json", "w") as out:
    json.dump(data, out, indent=2)
