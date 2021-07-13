'''
# walks a directory of pictures and resizes them for screen display

Author: Howard Webb
Date: 2/12/2021

'''

import os
from datetime import datetime, timedelta
from PIL import Image, ImageOps
from variables import height, width

dir = "/home/pi/pictures/"
out_dir = "/home/pi/Pictures/lapse/"
type = "jpg"

def get_all_images(dir, type, test=False):
    images = []
    for file in sorted(os.listdir(dir)):
        if file.endswith(type):
            images.append(Image.open(dir + file))
    return images

def resize(images, out_dir):
    x = 0
    for image in images:
        img = ImageOps.pad(image.convert("RGB"),
                     (width, height),
                     method=Image.NEAREST,
                     color=(0, 0, 0),
                     centering=(0.5, 0.5))
        img.save(out_dir + "{:02d}".format(x) + ".jpg")
        x += 1


if __name__=="__main__":
    print("Get All Images")
    images = get_all_images(dir, type)
    print("Found", len(images))
    print("Resize")
    resize(images, out_dir)
    print("Done")
