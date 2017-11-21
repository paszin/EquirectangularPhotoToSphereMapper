import math
'''
solid name
 facet normal n1 n2 n3
  outer loop
   vertex p1x p1y p1z
   vertex p2x p2y p2z
   vertex p3x p3y p3z
  endloop
 endfacet
endsolid name
'''

def normalize(vec):
    abs_vec = math.sqrt(sum(map(lambda x: pow(x, 2), vec)))
    return map(lambda x : x/abs_vec, vec)

def rotateX(v, a):
    x, y, z = v
    return x, math.cos(a)*y-math.sin(a)*z, math.sin(a)*y+math.cos(a)*z

def rotateY(v, a):
    x, y, z = v
    return math.cos(a)*x+math.sin(a)*z, y, -math.sin(a)*x+math.cos(a)*z

def rotateZ(v, a):
    x, y, z = v
    return math.cos(a)*x-math.sin(a)*y, math.sin(a)*x+math.cos(a)*y, z
    

def translate(v, x, y, z):
    return v[0]+x, v[1]+y, v[2]+z

class STLWriter:

    def __init__(self, name="object"):
        self.stl = ''
        self.name = name

    def start(self):
        self.stl += 'solid ' + self.name + '\n'
       
    def addFacet(self, v1, v2, v3):
        x1, y1, z1 = v1
        x2, y2, z2 = v2
        x3, y3, z3 = v3
        vector1 = [x2 - x1, y2 - y1, z2 - z1]
        vector2 = [x3 - x1, y3 - y1, z3 - z1]
        cross_product = [vector1[1] * vector2[2] - vector1[2] * vector2[1], -1 * (vector1[0] * vector2[2] - vector1[2] * vector2[0]), vector1[0] * vector2[1] - vector1[1] * vector2[0]]
        a = cross_product[0]
        b = cross_product[1]
        c = cross_product[2]
        d = - (cross_product[0] * x1 + cross_product[1] * y1 + cross_product[2] * z1)
        normal = normalize([a, b, c]) 
        self.stl += '\tfacet normal ' + ' '.join(map(str, normal)) + '\n'
        self.stl += '\t\touter loop\n'
        self.stl += '\t\t\tvertex ' + ' '.join(map(str, v1)) + '\n'
        self.stl += '\t\t\tvertex ' + ' '.join(map(str, v2)) + '\n'
        self.stl += '\t\t\tvertex ' + ' '.join(map(str, v3)) + '\n'
        self.stl += '\t\tendloop\n'
        self.stl += '\tendfacet\n'

    def finish(self):
        self.stl += 'endsolid ' + self.name

    def plane(self, v1, v2, v3, v4):
        self.addFacet(v1, v2, v3)
        self.addFacet(v3, v4, v1)
        

    def addCube(self, x, y, z, center=[0,0,0], rotX=None, rotY=None, rotZ=None):
        
        cx, cy, cz = 0, 0, 0
        x2, y2, z2 = x/2.0, y/2.0, z/2.0
        planes = [  [[cx-x2,cy-y2,cz-z2], [cx+x2,cy-y2,cz-z2], [cx+x2,cy-y2,cz+z2], [cx-x2, cy-y2, cz+z2]],
                    [[cx+x2,cy-y2,cz-z2], [cx+x2,cy+y2,cz-z2], [cx+x2,cy+y2,cz+z2], [cx+x2, cy-y2, cz+z2]],
                    [[cx-x2,cy-y2,cz-z2], [cx+x2,cy-y2,cz-z2], [cx+x2,cy-y2,cz+z2], [cx-x2, cy-y2, cz+z2]],
                    [[cx+x2,cy-y2,cz-z2], [cx+x2,cy+y2,cz-z2], [cx+x2,cy+y2,cz+z2], [cx+x2, cy-y2, cz+z2]],
                    [[cx-x2,cy-y2,cz+z2], [cx+x2,cy-y2,cz+z2], [cx+x2,cy+y2,cz+z2], [cx-x2, cy+y2, cz+z2]],
                    [[cx-x2,cy-y2,cz-z2], [cx+x2,cy-y2,cz-z2], [cx+x2,cy+y2,cz-z2], [cx-x2, cy+y2, cz-z2]],
                    [[cx-x2,cy-y2,cz-z2], [cx-x2,cy+y2,cz-z2], [cx-x2,cy+y2,cz+z2], [cx-x2, cy-y2, cz+z2]],
                    [[cx-x2,cy+y2,cz-z2], [cx+x2,cy+y2,cz-z2], [cx+x2,cy+y2,cz+z2], [cx-x2, cy+y2, cz+z2]]]
        for p in planes:
            p = map(lambda v: rotateX(v, rotX), p)
            p = map(lambda v: rotateY(v, rotY), p)
            p = map(lambda v: rotateZ(v, rotZ), p)
            p = map(lambda v: translate(v, *center), p)
            self.plane(*p)
                    



if __name__ == '__main__':
    s = STLWriter()
    s.start()
    #for i in range(1, 100):
    s.addCube(10, 10, 10, rotX=0, rotY=0, rotZ=0, center=[0,0,0])
    s.addCube(10, 10, 10, rotX=0, rotY=0, rotZ=math.pi/4, center=[20, 0, 0])
    s.finish()
    with open("demo.stl", "w") as f:
        f.write(s.stl)
