import bpy
import math

#  A                             C
#  _______________________________
#  |         /\        |        /| 
#  |        /| \       |       / | 
#  |       / |  \      |      /  | 
#  |      /  |   \     G     /   | 
#  |     /   |    \    |    /    | 
#  |    /    |     \   |   /     | 
#  |   /     E      \  |  /      | 
#  |  /      |       \ | /       | 
#  | /       |        \|/        | 
#  |/________|_________/_________|
#  B         F         H         D
# 
# EB = 1 (radius 1 cone with three points in its base)
# <ABC = pi / 6 (30 degrees or half the angle of an equilateral triangle)
# BH = FD = 2 cos(pi/6)
# AB = CD = 3 sin(pi/6) 
# EF = GH = 1 sin(pi/6)

BH = 2 * math.cos(math.pi/6)
EF = math.sin(math.pi/6)
AB = 3 * EF

def tetra_grid(side):
    up_tetras = []
    down_tetras = []
    for i in range(side):
        for j in range(side):
            bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=1, radius2=0, depth=1, 
                    location = (BH*(i-0.5*side), AB*(j-0.5*side), 0),
                    rotation = (0,0,0))
            up_tetras.append(bpy.context.object)

            bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=1, radius2=0, depth=1,
                    location = (BH*(i-0.5*side) + BH/2, AB*(j-0.5*side) + EF, 0),
                    rotation = (0,0,math.pi))
            down_tetras.append(bpy.context.object)

    return up_tetras, down_tetras

def scaler(tetras):
    for frame in range(100):
        for tetra in tetras:
            x,y,z = tetra.location
            x /= 5
            y /= 5
            scale_factor = abs(math.sin(frame * math.pi / 10 + math.sqrt(x*x + y*y)))
            tetra.scale = (scale_factor, scale_factor, scale_factor)
            tetra.keyframe_insert('scale', frame = frame * 10)

def roto_scaler(rot_scl_tetras, scl_tetras, keyframe_offset=0):
    a = math.sin(math.pi / 6)
    for tetra in rot_scl_tetras:
        tetra.rotation_mode = 'AXIS_ANGLE'
        frames = 20
        for frame in range(frames):
            angle = (frame / frames) * (math.pi / 3)
            tetra.rotation_axis_angle = (math.pi + angle, 0,0,1)
            tetra.keyframe_insert('rotation_axis_angle', frame = keyframe_offset + frame * 10)
            # original scale - the scale change
            scale = a / math.cos(math.pi/3 - angle)
            tetra.scale = (scale, scale, 1)
            tetra.keyframe_insert('scale', frame = keyframe_offset + frame * 10)

    return

    for tetra in scl_tetras:
        tetra.scale = (1, 1, 1)
        tetra.keyframe_insert('scale', frame = 0)

        # 
        #scale = 1-math.cos(math.pi/3) / 2
        #tetra.scale = (scale, scale, 1)
        #tetra.keyframe_insert('scale', frame = 20)

        tetra.scale = (1, 1, 1)
        tetra.keyframe_insert('scale', frame = 40)



def test():
    up_tetras, down_tetras = tetra_grid(5)
    all_tetras = up_tetras.copy()
    all_tetras.extend(down_tetras)
    #scaler(all_tetras)
    roto_scaler(down_tetras, up_tetras)

    return
    a = math.sin(math.radians(30))
    print("sin 30 = %s"%a)
    for i in range(0,61,10):
        print("%s : %s"%(i,a / math.cos(math.radians(i))))
    return



    
test()
