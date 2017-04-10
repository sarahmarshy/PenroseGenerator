
import cmath
import math
import svgwrite
import itertools
from svgwrite import mm, cm
import sys
import numpy as np

width = 200
height = 200

goldenRatio = (1 + math.sqrt(5)) / 2

class Point:
    def __init__(self, val, color):
        self.val = val
        self.color = color


def print_coords(coord):
    for thing in coord:
        l  = [cmath.polar(x) for x in thing]
        print '%s,%s,%s,%s'%(l[0],l[1],l[2],l[3])

def pol_to_arr(A):
    return np.array([A.real, A.imag])

def lin_coord(A):
    return A.real,A.imag

def dist(A, B):    
    ax, ay = lin_coord(A)
    bx, by = lin_coord(B)
    det = (bx-ax)**2+(by-ay)**2
    return math.sqrt(det)

def max_min(orig,A,B):
    if(dist(orig,A)  > dist(orig,B)):
        return A,B
    return B,A

def project(orig, target, size):
    v1 = pol_to_arr(orig)
    v2 = pol_to_arr(target)
    dx = (v2[0]-v1[0])
    dy = (v2[1]-v1[1])
    d2 = dist(orig,target)
    x = v1[0] + size/d2*dx
    y = v1[1] + size/d2*dy
    return complex(x, y)

def subdivide(triangles):
    result = []
    for color, A, B, C in triangles:
        if color == 0:
            right_edge = B if B.color == A.color else C
            left_edge = B if B.color != A.color else C
            sz = dist(right_edge.val, left_edge.val)
            P = project(A.val, right_edge.val, sz)
            Q = project(A.val, left_edge.val, sz/goldenRatio)
            pP = Point(P, A.color)
            pQ = Point(Q, not A.color)
            pA = Point(A.val, not A.color)
            pC = Point(left_edge.val, A.color)
            pB = Point(right_edge.val, not A.color)
            result += [(0, pC, pQ, pP), (0, pC, pB, pP), (1,pA,pP, pQ)] 
        else: 
            b_edge = B if B.color != A.color else C
            a_edge = B if B.color == A.color else C
            P = project(A.val, b_edge.val, dist(A.val,b_edge.val)/goldenRatio)
            x = [(1, b_edge, Point(P, b_edge.color), a_edge), (0, A, Point(P,b_edge.color), a_edge)]
            result += x
    return result

def initial_star(x, size):
    triangles = []
    for i in xrange(x):
        aColor = False
        bColor = True
        s1 = size
        s2 = size/goldenRatio
        if(i%2 != 0):
            aColor = True       
            bColor = False        
            s1 = s2
            s2 = size  
        A = cmath.rect(s1, (2*i)*math.pi/x)     
        B = cmath.rect(s2, (2*i+2)*math.pi/x)
        triangles.append([1, Point(0j, 1), Point(A, aColor), Point(B, bColor)])
    return triangles


def initial_triangles(x, size):
    triangles = []
    vcolor = True
    for i in xrange(x):
        A = cmath.rect(size, (2*i)*math.pi/x)
        B = cmath.rect(size, (2*i+2)*math.pi/x)
        if i%2 == 0:
            vcolor = False 
            A,B = B,A
        triangles.append([0, Point(0j,0), Point(A,not vcolor), Point(B, vcolor)])
    return triangles

def draw(triangles, fname, sz):
    dwg = svgwrite.Drawing(fname, profile='tiny', size=(sz,sz))
    shapes = dwg.add(dwg.g(id='shapes', fill='red'))
    for t in triangles:
        color = t[0]
        color = 'blue' if t[0] == 1 else 'red'
        coords = [p.val for p in t[1:]]
        points = [(sz/2+p.real, sz/2+p.imag) for p in coords]
        dwg.add(dwg.polygon(points=points, fill = color, stroke='black',
                          stroke_width=0.1))
    dwg.save()

if __name__ == "__main__":
    if sys.argv[1] == 'star':
        t = initial_star(10,100)
    elif sys.argv[1] == 'tri':
        t = initial_triangles(10,100)
    else:
        sys.exit(1)
    for x in range(int(sys.argv[2])):
        t = subdivide(t)

    draw(t, sys.argv[3], 200)
