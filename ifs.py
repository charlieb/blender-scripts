import bpy
import math
import mathutils
import copy
import random

def ifs(transforms, npoints, ignore_first_n=100, pt = mathutils.Vector((0,0,0,1))):
    dets = [t.determinant() for t in transforms]
    total_dets = sum(dets)
    dets = [d/total_dets for d in dets]
    for n in range(npoints):
        r = random.random()
        total = dets[0]
        trans = 0
        while total < r:
            trans += 1
            total += dets[trans]
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
    verts.extend(
            [(pos.x + 0.01, pos.y, pos.z),
             (pos.x, pos.y + 0.01, pos.z),
             (pos.x, pos.y, pos.z + 0.01)])
    faces.append((len(verts) -1, len(verts) -2, len(verts) -3))

def generate_ifs(npoints):
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
