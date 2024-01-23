import os
import bpy
# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty
from bpy.types import Operator

import numpy as np
from plyfile import PlyData, PlyElement


def write_ply_data(context, filepath, format_ascii):
    obj = bpy.context.active_object
    mats = obj.data.materials

    vertices = [ (vertex.co.x, vertex.co.y, vertex.co.z, vertex.normal.x, vertex.normal.y, vertex.normal.z) for vertex in obj.data.vertices ]
    faces = [ tuple([tuple([ vertex for vertex in face.vertices ]), face.normal.x, face.normal.y, face.normal.z] + [ int(round(i*255, 0)) for i in mats[face.material_index].node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value ]) for face in obj.data.polygons ]

    vertex = PlyElement.describe(np.array(vertices, dtype=[('x', 'f4'), ('y', 'f4'), ('z', 'f4'), ('nx', 'f4'), ('ny', 'f4'), ('nz', 'f4')]), 'vertex')
    face = PlyElement.describe(np.array(faces, dtype=[('vertex_indices', 'i4', (3,)), ('fx', 'f4'), ('fy', 'f4'), ('fz', 'f4'), ('red', 'u1'), ('green', 'u1'), ('blue', 'u1'), ('alpha', 'u1')]), 'face')

    with open(filepath, mode='wb') as f:
        PlyData([vertex, face], text=format_ascii).write(f)

    return {'FINISHED'}


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


def menu_func_export(self, context):
    self.layout.operator(ExportPLY.bl_idname, text="Export PLY")
