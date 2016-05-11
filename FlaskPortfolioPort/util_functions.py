import datetime
import io
from PIL import Image, ImageFont, ImageDraw
from collections import defaultdict
import heapq
import string

def age():                                               
     years_since = lambda date, today: int( (today - date).days /365.2425 ) #off by a bit
     return years_since( datetime.date(day=11, month=6, year=1995), datetime.date.today() )


def draw_memetext((h, w), caption, TOP=False):
    """Creates a blank image with memetext of a given size."""
    textimg = Image.new('RGBA', (h,w), (255,255,255,0))
    textdraw = ImageDraw.Draw(textimg)

    #find ideal font size
    size = 200
    memefont = ImageFont.truetype('./static/fonts/impact.ttf', size=size)
    tw, th = textdraw.textsize(longertext, font=memefont)
    while ( tw > w ):
        size -= 4
        memefont = ImageFont.truetype('./static/fonts/impact.ttf', size=size)
        tw, th = textdraw.textsize(longertext, font=memefont)
   
    draw_height = 0 if top else h - th

    #Draw black outline
    for i, j in zip(range(-1,2), range(-1,2)): #black outline
        textdraw.text( ((fw/2) - (tw/2) -i, draw_height-j), caption1, font=memefont, fill=(0,0,0,255))

    #draw text
    textdraw.text( ((fw/2) - (w/2), draw_height), caption1, font=memefont, fill=(255,255,255,255))

    return textimg

def meme( caption1, caption2 ):
    fatty = Image.open("./static/content/fatty.jpg").convert('RGBA')
    memefont = ImageFont.truetype('./static/fonts/impact.ttf', size=200)

    longertext = caption1 if len(caption1)>len(caption2) else caption2

    textimg = Image.new('RGBA', fatty.size, (255,255,255,0))
    textdraw = ImageDraw.Draw(textimg)
    fw, fh = fatty.size

    #find ideal font size
    size = 200
    w, h = textdraw.textsize(longertext, font=memefont)
    while ( w > fh ):
        size -= 4
        memefont = ImageFont.truetype('./static/fonts/impact.ttf', size=size)
        w, h = textdraw.textsize(longertext, font=memefont)

    for i, j in zip(range(-1,2), range(-1,2)): #black outline
        textdraw.text( ((fw/2) - (w/2) -i, 0 -j), caption1, font=memefont, fill=(0,0,0,255))
        textdraw.text(((fw/2) - (w/2) -i, fh-h-j), caption2, font=memefont, fill=(0,0,0,255))

    textdraw.text( ((fw/2) - (w/2), 0), caption1, font=memefont, fill=(255,255,255,255))
    textdraw.text(((fw/2) - (w/2), fh-h), caption2, font=memefont, fill=(255,255,255,255))
    
    outimg = Image.alpha_composite(fatty, textimg)
    outfile = io.BytesIO()
    outimg.save(outfile, format='jpeg')

    outfile.seek(0)
    return outfile

