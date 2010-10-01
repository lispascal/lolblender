import bpy
from bpy.props import *
from io_utils import ImportHelper
from sys import stderr
bl_addon_info = {
    'name': 'Import a League of Legends Skeleton file (.skl)',
    'author': 'Zac Berkowitz',
    'version': '0.0',
    'blender': (2,5,3),
    'location': 'File > Import',
    'category': 'Import/Export',
    }

__bpydoc__ = """
Import League of Legends Skeleton file (.skl)
"""

class bl_importSKL(bpy.types.Operator, ImportHelper):
    bl_idname = 'import_scene.lol_skl'
    bl_label = 'Import SKL'

    filename_ext = '.skl'
    filter_glob = StringProperty(default='*.skl', options={'HIDDEN'})

    def execute(self, context):
        #print('Selected: ' + context.active_object.name)
        print(self.filepath, file=stderr)
        import lolSkeleton
        header, boneDict = lolSkeleton.importSKL(self.filepath)
        #wolfFile = '/var/tmp/downloads/lol/Wolfman/Wolfman.skl'
        #header, boneDict = lolSkeleton.importSKL(wolfFile)
        lolSkeleton.buildSKL(boneDict)
        return{'FINISHED'}


def menu_func_import(self,context):
    self.layout.operator(bl_importSKL.bl_idname, text='LoL SKeleton (.skl)')

def register():
    bpy.types.INFO_MT_file_import.append(menu_func_import)

def unregister():
    bpy.types.INFO_MT_file_import.remove(menu_func_import)


if __name__ == '__main__':
    register()
