bl_info = {
    "name": "Import PLY file",
    "blender": (3, 6, 0),
    "category": "Import-Export",
}


import os
import bpy
import bmesh
# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from bpy.types import Operator

from plyfile import PlyData, PlyElement


def read_some_data(context, filepath):
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
    bpy.context.collection.objects.link(mesh_obj)
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


class ImportPLY(Operator, ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "import_ply.some_data"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import PLY"

    # ImportHelper mixin class uses this
    filename_ext = ".ply"

    filter_glob: StringProperty(
        default="*.ply",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        return read_some_data(context, self.filepath)


# Only needed if you want to add into a dynamic menu.
def menu_func_import(self, context):
    self.layout.operator(ImportPLY.bl_idname, text="Import PLY")


# Register and add to the "file selector" menu (required to use F3 search "Text Import Operator" for quick access).
def register():
    bpy.utils.register_class(ImportPLY)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportPLY)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.import_ply.some_data('INVOKE_DEFAULT')
