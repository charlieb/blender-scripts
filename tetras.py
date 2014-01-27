import bpy
import math
import mathutils
import copy

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

def roto_scale(tetra, relative_rotation, absolute_rotation):
    tetra.rotation_axis_angle = (absolute_rotation, 0,0,1)
    scale = a / math.cos(math.pi/3 - relative_rotation)
    tetra.scale = (scale, scale, scale)

def relative_roto_scaler(tetras, rotation, num_keyframes=20, keyframe_offset=0):
    '''
    Rotates and scales teselated equilateral triangles so the rotated versions still fit within their original boundries.
    Uses only relative rotation as basis for scaling so
    only use for complete rotations X*2*math.pi/3
    '''
    a = math.sin(math.pi / 6)
    for tetra in tetras:
        rot_per_frame = rotation / (num_keyframes - 1)
        angle = 0
        tetra.rotation_mode = 'XYZ'
        # back off one iteration so that the 0th frame will be
        # at the current rotation
        tetra.rotation_euler.rotate_axis('Z', -rot_per_frame)
        for frame in range(num_keyframes):
            tetra.rotation_euler.rotate_axis('Z', rot_per_frame)
            tetra.keyframe_insert('rotation_euler', frame = keyframe_offset + frame)

            scale = a / math.cos(math.pi/3 - angle)
            tetra.scale = (scale, scale, scale)
            tetra.keyframe_insert('scale', frame = keyframe_offset + frame)

            #print("%s) frame %s, angle: %s, scale %s, XYZ %s\n"%(tetra.name, frame, angle, scale, tetra.rotation_euler))
            angle += rot_per_frame

def roto_scaler(tetras, rotation, angle_offset=0, num_keyframes=20, frames_between_keyframes=2, keyframe_offset=0):
    '''
    Rotates and scales teselated equilateral triangles so the rotated versions still fit within their original boundries.
    Uses absolute rotation as basis for scaling so any angle can be used
    but the original orientation (angle_offset) must be supplied
    '''
    a = math.sin(math.pi / 6)
    for tetra in tetras:
        tetra.rotation_mode = 'AXIS_ANGLE'
        start_angle = tetra.rotation_axis_angle[0]
        start_scale = tetra.scale[0]
        for frame in range(num_keyframes):
            angle = start_angle - angle_offset + rotation * frame / (num_keyframes - 1)
            tetra.rotation_axis_angle = (angle + angle_offset, 0,0,1)
            tetra.keyframe_insert('rotation_axis_angle', frame = (keyframe_offset + frame) * frames_between_keyframes)
            scale = a / math.cos(math.pi/3 - angle)
            scale = 1
            tetra.scale = (scale, scale, scale)
            tetra.keyframe_insert('scale', frame = (keyframe_offset + frame) * frames_between_keyframes)
            #if tetra == tetras[0]:
            #    print("%s angle: %s - %s + %s = %s\n"%(frame, start_angle, angle_offset, (frame / num_keyframes) * rotation, angle))

############ OBJECT TO TETRAS ###############
def alignment_matrix(v1, v2):
    '''
    Returns a rotation matrix that aligns the first vector to the second
    '''
    axis = v1.cross(v2)
    angle = math.acos(v1.dot(v2))
    return mathutils.Matrix.Rotation(angle, 4, axis)

def transform_object_container(obj, matrix):
    '''Transforms the origin of a shape without transforming the shape''' 
    # transform the object
    obj.matrix_local = obj.matrix_local * matrix
    # transform the mesh
    obj.data.transform(matrix.inverted())

def polygon_to_tetra(poly, mesh):
    '''
    Converts a triangular polygon that is part of a mesh to a tetrahedron
    whos base is the original triangle and apex is side length along
    the normal from the polygon's origin
    '''
    # create a new mesh
    me = bpy.data.meshes.new("Tetra%s"%poly.index)
    # create a new object from the mesh
    ob = bpy.data.objects.new("Tetra", me)
    # Add the object to the scene
    bpy.context.scene.objects.link(ob) 
    # copy the coords from the poly (triangle) to the new mesh
    pc = poly.center
    '''
    print(list(pc))
    print(((mesh.data.vertices[0].co.x + mesh.data.vertices[1].co.x + mesh.data.vertices[2].co.x) / 3,
           (mesh.data.vertices[0].co.y + mesh.data.vertices[1].co.y + mesh.data.vertices[2].co.y) / 3,
           (mesh.data.vertices[0].co.z + mesh.data.vertices[1].co.z + mesh.data.vertices[2].co.z) / 3))
    print('-------------')
    '''
    coords = [(
        mesh.data.vertices[idx].co.x - pc[0],
        mesh.data.vertices[idx].co.y - pc[1],
        mesh.data.vertices[idx].co.z - pc[2])
            for idx in poly.vertices]
    # find the length of one side
    dx = coords[0][0] - coords[1][0]
    dy = coords[0][1] - coords[1][1]
    dz = coords[0][2] - coords[1][2]
    # use that length to scale the normal
    # TODO: calculate the corred scale: this is too long
    # because it's the distance between the center of the face and the apex
    # but here calculated is just the side length
    scl = math.sqrt(dx*dx + dy*dy + dz*dz)
    # add the top of the tetra along the normal direction of the poly
    pn = poly.normal
    coords.append((pn.x * scl, pn.y * scl, pn.z * scl))
    # build faces from vector indeces
    faces = [(0,1,2), (0,1,3), (1,2,3), (2,0,3)]
    me.from_pydata(coords,[],faces)
    me.update(calc_edges=True)

    # Align the local z of the mesh to the poly's normal
    am = alignment_matrix(mathutils.Vector((0,0,1)), poly.normal)
    transform_object_container(ob, am)
    # center the object on the poly
    ob.location = poly.center

    return ob

def mesh_to_tetras(mesh, splitter = lambda f: f.index % 2 == 0):
    '''
    Converts an entire mesh to tetrahedrons with polygon_to_tetra.
    Splits the list of new tetrahedrons into two lists
    '''
    up_tetras = []
    down_tetras = []
    for p in mesh.data.polygons:
        if splitter(p):
            up_tetras.append(polygon_to_tetra(p, mesh))
        else:
            down_tetras.append(polygon_to_tetra(p, mesh))
    return up_tetras, down_tetras

########### SPHERE SHIVER ##########

def shiver_along_axis(tetras):
    frames_per = 10
    steps = 60
    z = z_end = tetras[0].location.z
    for t in tetras:
        if t.location.z > z: z = t.location.z
        if t.location.z < z_end: z_end = t.location.z
    z_step = (z_end - z) / steps
    for frame in range(steps):
        tets = [tetra for tetra in tetras 
                if tetra.location.z <= z and 
                    tetra.location.z >= z + z_step]
        relative_roto_scaler(tets,
            2 * math.pi / 3,
            num_keyframes = 25,
            keyframe_offset = 2 * frame)
        print(z)
        z += z_step


def shiver():
    tetras, _ = mesh_to_tetras(bpy.context.object, splitter=lambda _: True)
    shiver_along_axis(tetras)




############ TESTINMG ############## 

def scaler_test(up_tetras, down_tetras):
    all_tetras = up_tetras.copy()
    all_tetras.extend(down_tetras)
    scaler(all_tetras)

def roto_scaler_test(up_tetras, down_tetras):
    roto_scaler(down_tetras, math.pi/3, angle_offset=math.pi, num_keyframes=10)
    roto_scaler(down_tetras, math.pi/3, angle_offset=math.pi, num_keyframes=10, keyframe_offset=9)
    roto_scaler(up_tetras, 2*math.pi/3, num_keyframes=20, keyframe_offset=18)

def test():
    up_tetras, down_tetras = mesh_to_tetras(bpy.context.object)
    #up_tetras, down_tetras = tetra_grid(15)

    #roto_scaler_test(up_tetras, down_tetras)
    # frames_between_keyframe=1 because the interpolation does weird things to
    # the rotation
    relative_roto_scaler(down_tetras, 2*math.pi/3, num_keyframes=30)
    relative_roto_scaler(up_tetras, 2*math.pi/3, num_keyframes=30, keyframe_offset=29)
    
