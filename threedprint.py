# -*- coding: utf-8 -*-
## this code is made for python2
import math
import numpy
from stl import mesh
from PIL import Image


def normalize(vec):
    abs_vec = math.sqrt(sum(map(lambda x: pow(x, 2), vec)))
    return map(lambda x : x/abs_vec, vec)

def scalar(vec1, vec2):
    return sum(map(lambda (a, b) : a*b, zip(vec1, vec2)))

def vlen(vec):
    return math.sqrt(scalar(vec, vec))

def angle(vec1, vec2):
    '''in degrees'''
    return math.acos(scalar(vec1, vec2)/(vlen(vec1)*vlen(vec2)))*360/(2*math.pi)

def rad2degree(a):
    return a*360/(math.pi*2)

def floatRange(start, stop, step):
    l = []
    while start < stop:
        l.append(start)
        start += step
    return l


class UVMapping:

    def __init__(self):
        self.image = Image.open("sofia.JPG")
        self.image = Image.open("chess.png").convert('RGB')
        #self.image = Image.new(
        
    def getUVMapping(self, x, y, z):
        x, y, z = normalize([x, y, z])
        u = math.atan2(x, z) / 2*math.pi + 0.5
        v = y * 0.5 + 0.5
        u *= self.image.size[0]
        v *= self.image.size[1]
        u = min(int(round(u)), self.image.size[1]-1)
        u = max(u, 0)
        v = min(int(round(v)), self.image.size[0]-1)
        v = max(v, 0)
        r, g, b = self.image.getpixel((v, u))
        return 1.0*r/255, 1.0*g/255, 1.0*b/255

    def getUVMapping2(self, x, y, z):
        u = x/vlen([x, y, z])
        v = y/vlen([x, y, z])
        u *= self.image.size[0]
        v *= self.image.size[1]
        u = min(int(round(u)), self.image.size[1]-1)
        u = max(u, 0)
        v = min(int(round(v)), self.image.size[0]-1)
        v = max(v, 0)
        r, g, b = self.image.getpixel((v, u))
        return 1.0*r/255, 1.0*g/255, 1.0*b/255
    

##r**2 - x**2 - y**2 = z**2

openscad_template = "color([{r}, {g}, {b}, 1]) " +\
                    "translate([{tx}, {ty}, {tz}])" +\
                    "rotate([{rx}, {ry}, {rz}])" +\
                    "cylinder(r=radius, h=0.1);"
#openscad_template = "color([{r}, {g}, {b}, 1]) translate([{tx}, {ty}, {tz}]) rotate([{rx}, {ry}, {rz}]) cube(radius, center=true);"


r = 1
rows = 6
columns = 2 * rows ## because of 2*pi
resolution = math.pi/rows #math.pi/72


## which rows to create
i_start = 175
i_end = 185

image =Image.open("sofia.JPG") 

out = ""
out += "$fn=12;\nradius={radius};\n".format(radius=resolution/2)
for i, phi in enumerate(floatRange(0, math.pi, resolution)):
    #if not i_start <= i < i_end:
    #    continue
    ##map to row in image
    crop = image.crop((0, i*image.size[1]/(rows+1), image.size[0], (i+1)*image.size[1]/(rows+1)))
    crop = crop.resize((columns, 1))
    for j, theta in enumerate(floatRange(0, 2*math.pi, math.pi/4)):
        x = math.sin(theta) * math.sin(phi)
        y = math.cos(theta) * math.sin(phi)
        z = math.cos(phi)
        ## rotation
        rx = 0
        ry = rad2degree(phi)
        rz = 90-rad2degree(theta)
        ## color
        #r = phi/math.pi
        #g = theta/(2*math.pi)
        #b = 0.5
        #r, g, b = mapping.getUVMapping2(x, y, z)
        r, g, b = map(lambda x: x/255.0, crop.getpixel((min(j, columns-1), 0)))
        out += openscad_template.format(tx=x, ty=y, tz=z, rx=rx, ry=ry, rz=rz, r=r, g=g, b=b)
        out += '\n'

with open("test.scad", 'w') as f:
    f.write(out)

print "done"


#for u in range(height):
 #   for v in range(width):
        ## normalisieren
        ##formeln von oben anwenden
        ##punkt auf der sphere finden vom stl import
        ##(distance punkt, fläche)
        ##verschiebe vertices entlang der normalen
        ##  um den grayscale wert
        ## --> es entstehen luecken, aber man sollte ein bild erkennen koennen


## alternative:
        ## berechnung wie oben
        ## neuen vertex erstellen
        ##verbinden mit vertex davor

##alternative
        ## openscad code erzeugen, rotate & translate cylinder
        
## alternative:
        ## openscad
        ##polyhedron( points = [ [X0, Y0, Z0], [X1, Y1, Z1], ... ], faces = [ [P0, P1, P2, P3, ...], ... ], convexity = N);
