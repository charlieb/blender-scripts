import bpy
import math

# filename = "/home/charlieb/src/blender/tetras.py"
# exec(compile(open(filename).read(), filename, 'exec'))

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

def move_current_origin(loc):
    # store the location of current 3d cursor  
    saved_location = bpy.context.scene.cursor_location.copy()  # returns a copy of the vector  
    # give 3dcursor new coordinates  
    bpy.context.scene.cursor_location = loc
    # set the origin on the current object to the 3dcursor location  
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')  
    # set 3dcursor location back to the stored location  
    bpy.context.scene.cursor_location = saved_location  

def tetra_grid(side):
    up_tetras = []
    down_tetras = []
    for i in range(side):
        for j in range(side):
            x, y = BH*(i-0.5*side), AB*(j-0.5*side)
            bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=1, radius2=0, depth=1, 
                    location = (x,y,0.5),
                    rotation = (0,0,0))
            move_current_origin((x,y,0))
            up_tetras.append(bpy.context.object)

            x, y = BH*(i-0.5*side) + BH/2, AB*(j-0.5*side) + EF
            bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=1, radius2=0, depth=1,
                    location = (x,y,0.5),
                    rotation = (0,0,math.pi))
            move_current_origin((x,y,0))
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

def roto_scaler(tetras, rotation, angle_offset=0, num_keyframes=20, frames_between_keyframes=2, keyframe_offset=0):
    a = math.sin(math.pi / 6)
    for tetra in tetras:
        tetra.rotation_mode = 'AXIS_ANGLE'
        start_angle = tetra.rotation_axis_angle[0]
        start_scale = tetra.scale[0]
        for frame in range(num_keyframes):
            angle = start_angle - angle_offset + rotation * frame / (num_keyframes - 1)
            tetra.rotation_axis_angle = (angle + angle_offset, 0,0,1)
            tetra.keyframe_insert('rotation_axis_angle', frame = (keyframe_offset + frame) * frames_between_keyframes)
            # original scale - the scale change
            scale = a / math.cos(math.pi/3 - angle)
            tetra.scale = (scale, scale, scale)
            tetra.keyframe_insert('scale', frame = (keyframe_offset + frame) * frames_between_keyframes)
            if tetra == tetras[0]:
                print("%s angle: %s - %s + %s = %s\n"%(frame, start_angle, angle_offset, (frame / num_keyframes) * rotation, angle))


def test():
    up_tetras, down_tetras = tetra_grid(15)
    all_tetras = up_tetras.copy()
    all_tetras.extend(down_tetras)
    #scaler(all_tetras)
    roto_scaler(down_tetras, math.pi/3, angle_offset=math.pi, num_keyframes=10)
    print('-----------------')
    roto_scaler(down_tetras, math.pi/3, angle_offset=math.pi, num_keyframes=10, keyframe_offset=9)
    roto_scaler(up_tetras, 2*math.pi/3, num_keyframes=20, keyframe_offset=18)


    
test()
