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


def ifs(transforms, npoints, ignore_first_n=100, pt = mathutils.Vector((0,0,0,1))):
    dets = [t.determinant() for t in transforms]
    total_dets = sum(dets)
    dets = [d/total_dets for d in dets]
    for trans, n in transform_order(transforms, npoints):
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


def generate_ifs_points(npoints):
    transforms = [object_transform(obj) for obj in bpy.context.selected_objects]
    
    # create a new mesh
    me = bpy.data.meshes.new("ifs")
    # create a new object from the mesh
    ob = bpy.data.objects.new("IFS", me)
    # Add the object to the scene
    bpy.context.scene.objects.link(ob) 
    for p in ifs(transforms, npoints+100, ignore_first_n=100):
        me.vertices.add(1)
        me.vertices[-1].co = (p.x, p.y, p.z)
    me.update()
    return me, ob

def regenerate_ifs_points(mesh):
    transforms = [object_transform(obj) for obj in bpy.context.selected_objects]
    i = 0
    for p in ifs(transforms, len(mesh.vertices)+100, ignore_first_n=100):
        #mesh.vertices[i].co = (p.x, p.y, p.z)
        mesh.vertices[i].co.x = p.x
        mesh.vertices[i].co.y = p.y
        mesh.vertices[i].co.z = p.z
        print("%s : %s"%(i,p))
        i += 1
    mesh.update()
    return mesh


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

def generate_ifs_animation(npoints, frame_start=0, frame_end=250):
    bpy.context.scene.frame_set(frame_start)
    mesh, obj = generate_ifs_points(npoints)
    obj.shape_key_add("IFS%s"%0)
    obj.data.shape_keys.key_blocks["IFS%s"%0].value = 0 / (frame_end - frame_start) 
    obj.data.shape_keys.key_blocks["IFS%s"%0].keyframe_insert('value')
    for fr in range(frame_start+1, frame_end):
        bpy.context.scene.frame_set(fr)
        mesh = regenerate_ifs_points(mesh)
        obj.shape_key_add("IFS%s"%fr)
        obj.data.shape_keys.key_blocks["IFS%s"%fr].value = fr / (frame_end - frame_start) 
        obj.data.shape_keys.key_blocks["IFS%s"%fr].keyframe_insert('value')


