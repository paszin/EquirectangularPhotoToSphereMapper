# -*- coding: utf-8 -*-
## this code is made for python2
import math
import time
import random
import os
import thread
import numpy
from stl import mesh
from PIL import Image

from stlwriter import STLWriter

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




##r**2 - x**2 - y**2 = z**2

openscad_template = "color([{r}, {g}, {b}, 1]) " +\
                    "translate([{tx}, {ty}, {tz}])" +\
                    "rotate([{rx}, {ry}, {rz}]) scale([1.05,1.05,1.05])"

#openscad_template += "cylinder(r=radius, h={h});"
openscad_template += " cube([radius*2, radius*2, {h}]);\n"



class LithoSphere:

    def __init__(self, filename, name=None):
        self.row_count = 10
        self.vertical_resolution = math.pi/self.row_count/2
        self.dot_radius = self.vertical_resolution/2
        self.image =Image.open(filename)
        if not name:
            self.image =Image.open(filename)
            self.name = filename.split('.')[0]
            self.folder = filename.split('.')[0] + str(random.randint(1, 1000))
            os.mkdir(self.folder)
            self.scad_folder = self.folder + '//' + 'scad'
            os.mkdir(self.scad_folder)
            self.stl_folder = self.folder + '//' + 'stl'
            os.mkdir(self.stl_folder)
        else:
            self.folder = name
            self.scad_folder = self.folder + '//' + 'scad'
            self.stl_folder = self.folder + '//' + 'stl'
            
        

    def calculate(self):
        size = 4
        for i in range(0, self.row_count, size):
            self.calculatePart((i, i+size), self.name+str(i))
    
    def calculatePart(self, rows, name):
        code = self.getOpenScadCode(rows)
        self.saveScadFile(code, self.scad_folder+'//ls_' + name)

    def renderStart(self):
        for f in os.listdir(self.scad_folder):
            command = "openscad " + self.scad_folder + "//" + f + \
                                " -o " + self.stl_folder +"//" + f.split('.')[0] + '.stl'
            thread.start_new_thread( os.system, (command, ) )

    def renderStartSingle(self, filename):
        command = "openscad " + self.scad_folder + "//" + filename + \
                                " -o " + self.stl_folder +"//" + filename.split('.')[0] + '.stl'
        thread.start_new_thread( os.system, (command, ) )
        

    def getRenderStatus(self):
        return len(os.listdir(self.stl_folder)), len(os.listdir(self.scad_folder))

    def waitForRendering(self, interval=60, singleRun=False, log=False):
        while True:
            if len(os.listdir(self.scad_folder)) == len(os.listdir(self.stl_folder)):
                break
            if singleRun or log:
                print str(len(os.listdir(self.stl_folder))) + " of " + str(len(os.listdir(self.scad_folder)))
            if singleRun:
                break
            time.sleep(interval)
        

    def mergeStls(self):
        name = "lithosphere_" + self.name + ".stl"
        with open(self.folder + '//' + name, "w") as fo:
            fo.write("solid Lithosphere\n")
            for fin in os.listdir(self.stl_folder):
                with open(self.stl_folder+'//' + fin) as fi:
                    content = fi.read()
                    content.replace("endsolid OpenSCAD_Model\n", "")
                    content.replace("solid OpenSCAD_Model\n", "")
                    fo.write(content)
            fo.write("endsolid Lithosphere\n")
        return name

        
        

    def getOpenScadCode(self, rows):

        rc = self.row_count ## refactor
        out = ""
        out += "$fn=6;\nradius={radius};\n".format(radius=self.dot_radius)
        for i, phi in enumerate(floatRange(0, math.pi, self.vertical_resolution)):
            if not rows[0] <= i < rows[1]:
                continue
            z = math.cos(phi)
            ##calculate number of dots in row
            x_tmp = math.sin(0) * math.sin(phi)
            y_tmp = math.cos(0) * math.sin(phi)
            r_row = vlen([x_tmp, y_tmp, 0])
            u_row = 2*math.pi*r_row
            dots_count = max(u_row/(2*self.dot_radius), 1)
            ##map to row in image
            crop = self.image.crop((0, i*self.image.size[1]/(rc+1), self.image.size[0], (i+1)*self.image.size[1]/(rc+1)))
            crop = crop.resize((int(round(dots_count)), 1))
            for j, theta in enumerate(floatRange(0, 2*math.pi, 2*math.pi/dots_count)):
                x = math.sin(theta) * math.sin(phi)
                y = math.cos(theta) * math.sin(phi)
                
                ## rotation
                rx = 0
                ry = rad2degree(phi)
                rz = 90 - rad2degree(theta)
                ## color
                #r, g, b = phi/math.pi, theta/(2*math.pi), 0.5
                r, g, b = map(lambda x: x/255.0, crop.getpixel((min(j, dots_count-1), 0)))
                grey = 0.216*r+0.7152*g+0.0722*b
                grey= (1-grey)*0.6+0.01 ##white=0.01, black=0.101
                out += openscad_template.format(tx=x, ty=y, tz=z, rx=rx, ry=ry, rz=rz, r=r, g=g, b=b, h=grey)
                out += '\n'
        return out

    def calculateStlCode(self):
        rc = self.row_count ## refactor
        stl = STLWriter()
        stl.start()
        for i, phi in enumerate(floatRange(0, math.pi, self.vertical_resolution)):
            z = math.cos(phi)
            ##calculate number of dots in row
            x_tmp = math.sin(0) * math.sin(phi)
            y_tmp = math.cos(0) * math.sin(phi)
            r_row = vlen([x_tmp, y_tmp, 0])
            u_row = 2*math.pi*r_row
            dots_count = max(u_row/(2*self.dot_radius), 1)
            ##map to row in image
            crop = self.image.crop((0, i*self.image.size[1]/(rc+1), self.image.size[0], (i+1)*self.image.size[1]/(rc+1)))
            crop = crop.resize((int(round(dots_count)), 1))
            for j, theta in enumerate(floatRange(0, 2*math.pi, 2*math.pi/dots_count)):
                x = math.sin(theta) * math.sin(phi)
                y = math.cos(theta) * math.sin(phi)
                
                ## rotation
                rx = 0
                ry = phi
                rz = math.pi/4 - theta
                ## color
                #r, g, b = phi/math.pi, theta/(2*math.pi), 0.5
                r, g, b = map(lambda x: x/255.0, crop.getpixel((min(j, dots_count-1), 0)))
                grey = 0.216*r+0.7152*g+0.0722*b
                grey= (1-grey)*0.6+0.01 ##white=0.01, black=0.101
                stl.addCube(x=2*self.dot_radius, y=2*self.dot_radius, z=2*self.dot_radius, center=[x, y, z], rotX=rx, rotY=ry, rotZ=rz)
        stl.finish()
        return stl.stl
        

    def saveScadFile(self, code, name):
        with open(name + ".scad", 'w') as f:
            f.write(code)



def process1():
    print "[" + time.strftime("%H:%M:%S") + "]"
    ls = LithoSphere("sofia.JPG")
    print "Working Directory: ", ls.folder
    print "Calculation start"
    ls.calculate()
    print "Calculation done"
    print "[" + time.strftime("%H:%M:%S") + "]"
    #ls.renderStart()
    print "Rendering in process"
    files = sorted(os.listdir(ls.scad_folder), cmp=lambda x, y : cmp(int(x.replace('ls_'+ls.name, '').replace('.scad', '')), int(y.replace('ls_' + ls.name, '').replace('.scad', ''))))
    for i, f in enumerate(files):
        ## wait...
        while ls.getRenderStatus()[0] + 3 < i:
            time.sleep(10)
        print "start rendering ", f
        ls.renderStartSingle(f)
    ls.waitForRendering(log=True, interval=120)
    print "Rendering done"
    print "[" + time.strftime("%H:%M:%S") + "]"
    print "Merge Stls start"
    outname = ls.mergeStls()
    print "Merge Stls done"
    print "[" + time.strftime("%H:%M:%S") + "]"
    print "\nALL DONE"
    print "File: ", outname

def process2():
    print "[" + time.strftime("%H:%M:%S") + "]"
    ls = LithoSphere("sofia.JPG", name="x")
    code = ls.calculateStlCode()
    with open("sofia_new_stl.stl", "w") as f:
        f.write(code)
    print 'done'
    print "[" + time.strftime("%H:%M:%S") + "]"
    

if __name__ == "__main__":
    process2()


    
    
    
