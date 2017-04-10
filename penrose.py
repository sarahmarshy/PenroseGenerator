import cmath
import math
import svgwrite
import sys

golden_ratio = (1 + math.sqrt(5)) / 2

class Point:
    def __init__(self, val, color):
        self.val = val
        self.color = color

def lin_coord(A):
    return (A.real,A.imag)

def dist(A, B):    
    ax, ay = lin_coord(A)
    bx, by = lin_coord(B)
    det = (bx-ax)**2+(by-ay)**2
    return math.sqrt(det)

def project(orig, target, size):
    v1 = lin_coord(orig)
    v2 = lin_coord(target)
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
            right_edge, left_edge = C, B
            if B.color == A.color:
                right_edge, left_edge = B, C
            
            sz = dist(right_edge.val, left_edge.val)
            P = project(A.val, right_edge.val, sz)
            Q = project(A.val, left_edge.val, sz/golden_ratio)
            
            pP = Point(P, A.color)
            pQ = Point(Q, not A.color)
            pA = Point(A.val, not A.color)
            pC = Point(left_edge.val, A.color)
            pB = Point(right_edge.val, not A.color)
            
            result += [(0, pC, pQ, pP), (0, pC, pB, pP), (1,pA,pP, pQ)] 
        else: 
            b_edge, a_edge = C, B
            if B.color != A.color:
                b_edge, a_edge = B, C
            
            P = project(A.val, b_edge.val, dist(A.val,b_edge.val)/golden_ratio)
            pP = Point(P, b_edge.color)
            result += [(1, b_edge, pP, a_edge), (0, A, pP, a_edge)]
    return result

def initial_star(x, size):
    triangles = []
    for i in xrange(x):
        s1 = size if i%2 == 0 else size/golden_ratio
        s2 = size/golden_ratio if i%2 == 0 else size

        A = cmath.rect(s1, (2*i)*math.pi/x)     
        B = cmath.rect(s2, (2*i+2)*math.pi/x)
        triangles.append([1, Point(0j, 1), Point(A, i%2!=0), Point(B, i%2==0)])
    return triangles


def initial_sun(x, size):
    triangles = []
    for i in xrange(x):
        A = cmath.rect(size, (2*i)*math.pi/x)
        B = cmath.rect(size, (2*i+2)*math.pi/x)
        if i%2 == 0: 
            A,B = B,A
        triangles.append([0, Point(0j,0), Point(A, 0), Point(B, 1)])
    return triangles

def draw(triangles, fname, sz):
    dwg = svgwrite.Drawing(fname, profile='tiny', size=(sz,sz))
    for t in triangles:
        color = 'blue' if t[0] == 1 else 'orange'
        coords = [p.val for p in t[1:]]
        points = [(sz/2+p.real, sz/2+p.imag) for p in coords]
        dwg.add(dwg.polygon(points=points, fill = color, stroke='black',
                          stroke_width=0.1))
    dwg.save()

if __name__ == "__main__":
    sz = 350
    if sys.argv[1] == 'star':
        t = initial_star(10,sz)
    elif sys.argv[1] == 'sun':
        t = initial_sun(10,sz)
    else:
        sys.exit(1)
    for x in range(int(sys.argv[2])):
        t = subdivide(t)

    draw(t, sys.argv[3], sz*2)
