bl_info = {
    "name": "Export PLY file",
    "blender": (3, 6, 0),
    "category": "Import-Export",
}


import os
import bpy
import bmesh
# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

from plyfile import PlyData, PlyElement


# int(round(0.44*255, 0))

def write_some_data(context, filepath, use_some_setting):
    print("running write_some_data...")
    f = open(filepath, 'w', encoding='utf-8')
    f.write("Hello World %s" % use_some_setting)
    f.close()

    return {'FINISHED'}


class ExportPLY(Operator, ExportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "export_ply.some_data"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Export PLY file"

    # ExportHelper mixin class uses this
    filename_ext = ".ply"

    filter_glob: StringProperty(
        default="*.ply",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    format: BoolProperty(
        name="Format",
        description="Exporting using ASCII file format, otherwise use binary format.",
        default=True,
    )

    def execute(self, context):
        return write_some_data(context, self.filepath, self.format)


# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
    self.layout.operator(ExportPLY.bl_idname, text="Export PLY")


# Register and add to the "file selector" menu (required to use F3 search "Text Export Operator" for quick access).
def register():
    bpy.utils.register_class(ExportPLY)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ExportPLY)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.export_ply.some_data('INVOKE_DEFAULT')
