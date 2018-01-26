import argparse
import cmath
import math
import svgwrite
import sys

golden_ratio = (1 + math.sqrt(5)) / 2
interior_angle = math.pi/5

class Point:
    def __init__(self, val, color):
        self.val = val
        self.color = color

# Get the linear coordinates from a complex number (Polar coordinate)
def lin_coord(A):
    return (A.real,A.imag)

# Find the distance between two Polar coordinates
def dist(A, B):    
    ax, ay = lin_coord(A)
    bx, by = lin_coord(B)
    det = (bx-ax)**2+(by-ay)**2
    return math.sqrt(det)

# Get a vector V of magnitude size in the direction of vector P1P2
def project(P1, P2, size):
    v1 = lin_coord(P1)
    v2 = lin_coord(P2)
    dx = (v2[0]-v1[0])
    dy = (v2[1]-v1[1])
    magnitude = dist(P1,P2)
    x = v1[0] + size/magnitude*dx
    y = v1[1] + size/magnitude*dy
    return complex(x, y)

# Given a set of triangles, divide them into sub-triangles according to P2 Penrose Tiling substitution rules
def subdivide(triangles):
    result = []
    for color, A, B, C in triangles:
        # Check the color of the triangle.
        # 0 indicates acute Robinson triangle, 1 is obtuse Robinson triangle
        if color == 0:
            # The actute triangle subdivides into two acute triangles, and one obtuse triangle
            # So we will introduce two addintional vertices, P and Q
            pbisect_edge, qbisect_edge = C, B
            if B.color == A.color:
                pbisect_edge, qbisect_edge = B, C
            
            # The size of the edge A->P will be the distance between the longer edges of the actue triangle, 
            # or the short side of the triangle
            sz = dist(pbisect_edge.val, qbisect_edge.val)
            P = project(A.val, pbisect_edge.val, sz)
            # The vectors A->P and A->Q make up the long and short sides of an obtuse Robinson triangle, respectively
            # so the size from A->Q must be |A->P|/golden ratio
            Q = project(A.val, qbisect_edge.val, sz/golden_ratio)
            
            # Recolor the vertices according to substitution rules
            pP = Point(P, A.color)
            pQ = Point(Q, not A.color)
            pA = Point(A.val, not A.color)
            pC = Point(qbisect_edge.val, A.color)
            pB = Point(pbisect_edge.val, not A.color)
            
            result += [(0, pC, pQ, pP), (0, pC, pB, pP), (1,pA, pP, pQ)] 
        else: 
            # The obtuse triangle subdivides into one acute triangle and one obtuse triangle
            # So we will introduce one additional vertex, P

            # We want to bisect the edge A->C or A->B, we want the ending vertex to be the opposite color of the A vertex
            bisect_edge, unmodified_edge = C, B
            if B.color != A.color:
                bisect_edge, unmodified_edge = B, C
            
            # The size of the new edge will be the magnitude of A->X/golden_ratio
            P = project(A.val, bisect_edge.val, dist(A.val,bisect_edge.val)/golden_ratio)
            pP = Point(P, bisect_edge.color)
            result += [(1, bisect_edge, pP, unmodified_edge), (0, A, pP, unmodified_edge)]
    return result

# generates polar coordinates of two edges of a Robinson triangle 
#  
# The angle between them is acute angle of both triangles-- 36 degrees) 
#
def init_vertex_pair(x, s1, s2):
     A = cmath.rect(s1, x*interior_angle)     
     B = cmath.rect(s2, (x+1)*interior_angle)
     return A, B 

# Initial triangles will be in a star configuration, x number triangles @ size size
def initial_star(x, size):
    triangles = []
    for i in xrange(x):
        # We will make an obtuse Robinson triangle
        # The short and long sides of Robinson triangle have ratio 1:golden ratio
        s1 = size if i%2 == 0 else size/golden_ratio
        s2 = size/golden_ratio if i%2 == 0 else size
        # They have a an angle of 36 degrees between them
        A, B = init_vertex_pair(i, s1, s2)
        triangles.append([1, Point(0j, 1), Point(A, i%2!=0), Point(B, i%2==0)])
    return triangles

# Initial triangles will be in a sun configuration, x number triangles @ size size
def initial_sun(x, size):
    triangles = []
    for i in xrange(x):
        # We will make an acute Robinson triangle
        # They have the same size, but an angle of 36 degrees between them
        A, B = init_vertex_pair(i, size, size)
        if i%2 == 0: 
            A,B = B,A
        triangles.append([0, Point(0j,0), Point(A, 0), Point(B, 1)])
    return triangles

def draw(triangles, color1, color2, color_stroke, fname, sz):
    dwg = svgwrite.Drawing(fname, profile='tiny', size=(sz,sz))
    for t in triangles:
        color = color1 if t[0] == 1 else color2
        coords = [p.val for p in t[1:]]
        points = [(sz/2+p.real, sz/2+p.imag) for p in coords]
        dwg.add(dwg.polygon(points=points, fill=color, stroke=color_stroke, stroke_width=0.5))
    dwg.save()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--shape', choices=('star', 'sun'), default='sun', help='')
    parser.add_argument('--number', default=5, type=int, help='')
    parser.add_argument('--color1', default='cyan', help='')
    parser.add_argument('--color2', default='rgb(255, 102, 0)', help='')
    parser.add_argument('--color_stroke', default='black', help='')
    parser.add_argument('--size', default=200, type=int, help='')
    parser.add_argument('--fname', default='beautiful', help='')
    args = parser.parse_args()

    sz = args.size
    number_generations = args.number
    color1 = args.color1
    color2 = args.color2
    color_stroke = args.color_stroke

    if args.shape == 'sun':
        t = initial_sun(10, sz)
    elif args.shape == 'star':
        t = initial_star(10, sz)
     
    draw(t, color1, color2, color_stroke, 'none.svg', sz*2)
    for x in range(number_generations):
        t = subdivide(t)
        fname = '%s%s.svg' % (args.fname, x)
        draw(t, color1, color2, color_stroke, fname, sz*2)
