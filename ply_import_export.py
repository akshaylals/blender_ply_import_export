bl_info = {
    "name": "Import and Export PLY file with face colors",
    "author": "Akshaylal S",
    "version": (1, 0, 0),
    "blender": (3, 6, 0),
    "location": "File > Import-Export",
    "category": "Import-Export",
}


import os
import bpy
import bmesh
from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy.props import StringProperty, BoolProperty
from bpy.types import Operator

import numpy as np
from plyfile import PlyData, PlyElement


def read_ply_data(context, filepath):
    filename = os.path.split(filepath)[1]
    print("running read_some_data...")
    data = PlyData.read(filepath)

    vertices = data['vertex']
    faces = data['face']

    bm = bmesh.new()
    verts = [bm.verts.new(v) for v in vertices[['x', 'y', 'z']]]

    for face in faces['vertex_indices']:
        face = [ verts[i] for i in face]
        bm.faces.new(face)
    
    me = bpy.data.meshes.new(f'{filename}.mesh')
    mesh_obj = bpy.data.objects.new(filename, me)
    context.collection.objects.link(mesh_obj)
    bm.to_mesh(me)
    bm.free()

    if all([ i in faces for i in ['red', 'green', 'blue', 'alpha']]):
        materials = dict()
        colors = [ (red, green, blue, alpha) for red, green, blue, alpha in faces[['red', 'green', 'blue', 'alpha']] ]
        mat_i_counter = 0
        for red, green, blue, alpha in colors:
            color = (red, green, blue, alpha)
            if not materials.get(color, False):
                mat = bpy.data.materials.new(f'{filename}.material')
                mat.use_nodes = True
                mat.node_tree.nodes['Principled BSDF'].inputs["Base Color"].default_value = [ i / 255 for i in color ]

                # set material to the object:
                mesh_obj.data.materials.append(mat)
                materials[color] = mat_i_counter
                mat_i_counter += 1
        for f, color in zip(me.polygons, colors):
            f.material_index = materials[color]

    return {'FINISHED'}

def write_ply_data(context, filepath, format_ascii):
    obj = context.active_object
    mats = obj.data.materials

    vertices = [ (vertex.co.x, vertex.co.y, vertex.co.z, vertex.normal.x, vertex.normal.y, vertex.normal.z) for vertex in obj.data.vertices ]
    faces = [ tuple([tuple([ vertex for vertex in face.vertices ]), face.normal.x, face.normal.y, face.normal.z] + [ int(round(i*255, 0)) for i in mats[face.material_index].node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value ]) for face in obj.data.polygons ]

    vertex = PlyElement.describe(np.array(vertices, dtype=[('x', 'f4'), ('y', 'f4'), ('z', 'f4'), ('nx', 'f4'), ('ny', 'f4'), ('nz', 'f4')]), 'vertex')
    face = PlyElement.describe(np.array(faces, dtype=[('vertex_indices', 'i4', (3,)), ('fx', 'f4'), ('fy', 'f4'), ('fz', 'f4'), ('red', 'u1'), ('green', 'u1'), ('blue', 'u1'), ('alpha', 'u1')]), 'face')

    with open(filepath, mode='wb') as f:
        PlyData([vertex, face], text=format_ascii).write(f)

    return {'FINISHED'}


class ImportPLY(Operator, ImportHelper):
    """Load PLY file"""
    bl_idname = "import_mesh.ply"
    bl_label = "Import PLY"

    # ImportHelper mixin class uses this
    filename_ext = ".ply"

    filter_glob: StringProperty(
        default="*.ply",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        return read_ply_data(context, self.filepath)


class ExportPLY(Operator, ExportHelper):
    """Save PLY file"""
    bl_idname = "export_mesh.ply"
    bl_label = "Export PLY file"

    # ExportHelper mixin class uses this
    filename_ext = ".ply"

    filter_glob: StringProperty(
        default="*.ply",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    format_ascii: BoolProperty(
        name="ASCII",
        description="Exporting using ASCII file format, otherwise use binary format.",
        default=True,
    )

    def execute(self, context):
        return write_ply_data(context, self.filepath, self.format_ascii)


def menu_func_import(self, context):
    self.layout.operator(ImportPLY.bl_idname, text="Import PLY")

def menu_func_export(self, context):
    self.layout.operator(ExportPLY.bl_idname, text="Export PLY")

def register():
    bpy.utils.register_class(ImportPLY)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.utils.register_class(ExportPLY)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_class(ImportPLY)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.utils.unregister_class(ExportPLY)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()

    # test call
    # bpy.ops.import_mesh.ply('INVOKE_DEFAULT')
