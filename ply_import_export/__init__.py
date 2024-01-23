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

from .ply_import import ImportPLY, menu_func_import
from .ply_export import ExportPLY, menu_func_export

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
