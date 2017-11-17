
import math
from PIL import Image

def radiusEarth(b):
    r1 = 6378.137
    r2 = 6356.752
    return math.sqrt((((r1**2*math.cos(b))**2)+(r2**2*math.sin(b))**2)/(((r1*math.cos(b))**2)+(r2*math.sin(b))**2))

def radius(b):
    r1 = 1
    r2 = 0.1
    #b = 2*math.pi/360*b
    return math.sqrt((((r1**2*math.cos(b))**2)+(r2**2*math.sin(b))**2)/(((r1*math.cos(b))**2)+(r2*math.sin(b))**2))


def map_range(x, min1, max1, min2, max2):
    return 1.0*x*(max2-min2)/(max1-min1)



def resizeBy(img, factor):
    return img.resize(tuple(map(lambda x : x/5, list(img.size))))
    
img = Image.open("sofia.JPG")

width, height = img.size

segments = 12

cropped_width, cropped_height = width/segments, height


globe = Image.new('RGB', img.size)

for si in range(segments):
    digon = Image.new('RGB', (cropped_width, cropped_height), color=0xffffff)
    area = (si*cropped_width, 0, (si+1)*cropped_width, height)
    cropped_img = img.crop(area)
    for i in range(cropped_height-1):
        b = map_range(i, 0, cropped_height, -1, 1)
        scale_factor = math.sqrt(1-min(abs(2.0*i/cropped_height-1), 1))
        #if i%10 == 0: print scale_factor
        new_width = max(int(round(scale_factor*cropped_width)), 1)
        pixel_row = cropped_img.crop((0, i, cropped_width, i+1))
        pixel_row = pixel_row.resize((new_width, 1))
        digon.paste(pixel_row, ((cropped_width/2-new_width/2), i))

    #resizeBy(digon, 5).show()    
    globe.paste(digon, (si*cropped_width, 0))



## make it a bit smaller to view
globe = resizeBy(globe, 5)
globe.show()
