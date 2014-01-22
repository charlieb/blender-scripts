import bpy
import math

def cube_grid(side):
    cubes = []
    for i in range(side):
        cubes.append([])
        for j in range(side):
            bpy.ops.mesh.primitive_cube_add()
            cube = bpy.context.object
            cube.location = (2.1*(i-0.5*side), 2.1*(j-0.5*side), 0)
            cubes[i].append(cube)
    return cubes
        

def scaler(cubes):
    for frame in range(100):
        for i in range(len(cubes)):
            for j in range(len(cubes[0])):
                x,y,z = cubes[i][j].location
                x /= 5
                y /= 5
                scale_factor = math.sin(frame * math.pi / 10 + math.sqrt(x*x + y*y))
                cubes[i][j].scale = (scale_factor, scale_factor, scale_factor)
                cubes[i][j].keyframe_insert('scale', frame = frame * 10)

def test():
    cubes = cube_grid(5)
    scaler(cubes)
    
test()
