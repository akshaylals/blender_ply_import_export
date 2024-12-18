import os
import bpy
import bmesh
# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from bpy.types import Operator

from plyfile import PlyData


def read_ply_data(context, filepath):
    filename = os.path.split(filepath)[1]
    print("running read_some_data...")
    data = PlyData.read(filepath)

    vertices = data['vertex']
    faces = data['face']

    bm = bmesh.new()
    verts = [bm.verts.new(v) for v in vertices[['x', 'y', 'z']]]

    skip_i = []

    for i, face in enumerate(faces['vertex_indices']):
        face = [ verts[j] for j in face ]
        try:
            bm.faces.new(face)
        except ValueError:
            skip_i.append(i)
            continue
    
    me = bpy.data.meshes.new(f'{filename}.mesh')
    mesh_obj = bpy.data.objects.new(filename, me)
    bpy.context.collection.objects.link(mesh_obj)
    bm.to_mesh(me)
    bm.free()

    if all([ i in faces for i in ['red', 'green', 'blue', 'alpha']]):
        materials = dict()
        colors = [ (red, green, blue, alpha) for i, (red, green, blue, alpha) in enumerate(faces[['red', 'green', 'blue', 'alpha']]) if i not in skip_i ]
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


def menu_func_import(self, context):
    self.layout.operator(ImportPLY.bl_idname, text="Import PLY")
