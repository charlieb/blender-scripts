import bpy
import math
import mathutils
import copy
import random

def transform_order(transforms, n):
    dets = [t.determinant() for t in transforms]
    total_dets = sum(dets)
    dets = [d/total_dets for d in dets]
    for i in range(n):
        r = random.random()
        total = dets[0]
        trans = 0
        while total < r:
            trans += 1
            total += dets[trans]
        yield(trans, i)


def ifs(transforms, npoints, ignore_first_n=100, pt = mathutils.Vector((0,0,0,1)), transform_order_cache=False):
    dets = [t.determinant() for t in transforms]
    total_dets = sum(dets)
    dets = [d/total_dets for d in dets]
    for trans, n in (transform_order_cache if transform_order_cache
                                           else transform_order(transforms, npoints)):
        pt = transforms[trans] * pt
        if n > ignore_first_n:
            yield(copy.deepcopy(pt))

def object_transform(obj):
    rot = obj.rotation_euler.to_matrix().to_4x4()
    tra = mathutils.Matrix.Translation(obj.location).to_4x4()
    scl = mathutils.Matrix.Identity(4)
    scl[0][0] = obj.scale[0]
    scl[1][1] = obj.scale[1]
    scl[2][2] = obj.scale[2]
    return scl * rot * tra

def add_triangle(pos, verts, faces):
    scl = 0.005
    rnd_x = (0.5 - random.random()) * scl
    rnd_y = (0.5 - random.random()) * scl
    rnd_z = (0.5 - random.random()) * scl
    verts.extend(
            [(pos.x + rnd_x, pos.y, pos.z),
             (pos.x, pos.y + rnd_y, pos.z),
             (pos.x, pos.y, pos.z + rnd_x)])
    faces.append((len(verts) -1, len(verts) -2, len(verts) -3))

def save_ifs_point_cloud(filename, npoints):
    """Writes an obj file"""
    transforms = [object_transform(obj) for obj in bpy.context.selected_objects]
    f = open(filename, 'w')
    
    for p in ifs(transforms, npoints+100, ignore_first_n=100):
        print("v %s %s %s"%(p.x, p.y, p.z), file=f)
    f.close()


def generate_ifs_points(npoints, transform_order_cache=False):
    transforms = [object_transform(obj) for obj in bpy.context.selected_objects]
    
    # create a new mesh
    me = bpy.data.meshes.new("ifs")
    # create a new object from the mesh
    ob = bpy.data.objects.new("IFS", me)
    # Add the object to the scene
    bpy.context.scene.objects.link(ob) 
    for p in ifs(transforms, npoints+100, ignore_first_n=100, transform_order_cache=transform_order_cache):
        me.vertices.add(1)
        me.vertices[-1].co = (p.x, p.y, p.z)
    me.update()
    return ob

def regenerate_ifs_points(vertices, transform_order_cache=False):
    transforms = [object_transform(obj) for obj in bpy.context.selected_objects]
    i = 0
    for p in ifs(transforms, len(vertices)+100, ignore_first_n=100, transform_order_cache=transform_order_cache):
        vertices[i].co = (p.x, p.y, p.z)
        #print("%s: %s"%(i,p))
        i += 1

def generate_ifs_object(npoints):
    transforms = [object_transform(obj) for obj in bpy.context.selected_objects]
    verts = []
    faces = []
    for p in ifs(transforms, npoints+100, ignore_first_n=100):
        add_triangle(p, verts, faces)
    
    # create a new mesh
    me = bpy.data.meshes.new("ifs")
    # create a new object from the mesh
    ob = bpy.data.objects.new("IFS", me)
    # Add the object to the scene
    bpy.context.scene.objects.link(ob) 
    me.from_pydata(verts,[],faces)
    me.update(calc_edges=True)
    return me

def generate_ifs_animation(npoints, frame_start=0, frame_end=250, transform_order_cache=False):
    bpy.context.scene.frame_set(frame_start)
    obj = generate_ifs_points(npoints, transform_order_cache=transform_order_cache)
    obj.shape_key_add("Basis")
    # Create the first shapekey
    for fr in range(frame_start, frame_end):
        bpy.context.scene.frame_set(fr)
        # Add a new shapekey
        key = obj.shape_key_add("IFS%s"%fr)
        key.value = 0
        key.keyframe_insert('value', frame=fr)
        # Move the vertices
        #obj.editmode_toggle()
        regenerate_ifs_points(key.data, transform_order_cache=transform_order_cache)
        #obj.editmode_toggle()
        # set the end of the previous shape key
        key.value = 1
        key.keyframe_insert('value', frame=fr+1)
        # unset the current shapekey so it doesn't screw up the next one
        key.value = 0
        key.keyframe_insert('value', frame=fr+2)

        print("Frame: %s"%fr)

def generate_ifs_animation_caching(npoints, frame_start=0, frame_end=250):
    transforms = [object_transform(obj) for obj in bpy.context.selected_objects]
    to = list(transform_order(transforms, npoints))
    print(len(to))
    generate_ifs_animation(npoints, frame_start=frame_start, frame_end=frame_end, transform_order_cache=to)
