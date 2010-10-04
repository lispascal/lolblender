import bpy
from bpy.props import *
from io_utils import ImportHelper
from sys import stderr
from os import path

import lolMesh, lolSkeleton
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


def import_char(MODEL_DIR="", SKN_FILE="", SKL_FILE="", DDS_FILE=None):

    SKN_FILEPATH=path.join(MODEL_DIR, SKN_FILE)
    SKL_FILEPATH=path.join(MODEL_DIR, SKL_FILE)
    DDS_FILEPATH=path.join(MODEL_DIR, DDS_FILE)

    sklHeader, boneDict = lolSkeleton.importSKL(SKL_FILEPATH)
    lolSkeleton.buildSKL(boneDict)

    sknHeader, materials, indices, vertices = lolMesh.importSKN(SKN_FILEPATH)
    lolMesh.buildMesh(SKN_FILEPATH)

    meshObj = bpy.data.objects['Mesh']
    armObj = bpy.data.objects['Armature']

    lolMesh.addDefaultWeights(boneDict, vertices, armObj, meshObj)
    
    armObj.selected = False
    if DDS_FILE:
        bpy.ops.object.mode_set(mode='EDIT')
        img = bpy.data.images.new(DDS_FILE)
        tex = bpy.data.textures.new('texture', type='IMAGE')
        mat = bpy.data.materials.new('material')

        img.filepath=DDS_FILEPATH
        img.source = 'FILE'

        meshObj.material_slots[0].material = mat
        mat.texture_slots.create(0)
        mat.texture_slots[0].texture = tex
        mat.texture_slots[0].texture_coords = 'UV'
        tex.image = img
        bpy.ops.object.mode_set(mode='OBJECT')

