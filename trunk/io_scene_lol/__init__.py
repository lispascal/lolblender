import bpy
from bpy.props import *
from io_utils import ImportHelper
from sys import stderr
from os import path, listdir

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

class ImportLoL_popup_dialog(bpy.types.Operator):
    bl_idname = 'import.lol_data'
    bl_label = 'Import LoL Data'

    sklEnum = [('a','a','a'),('b','b','b')]
    sknEnum = []
    texEnum = []

    DIRECTORY = StringProperty(name='Model Directory', 
            description='''Root directory for the model containing mesh, skeleton,
            and texture files''', default = '', subtype='DIR_PATH')
    LOAD_WEIGHTS = BoolProperty(name='Load Weights', description='''Import mesh
    deformation weights from model file''', default=False)

    SKN_FILES = EnumProperty(name='Model Files', 
            description='Available Model Files', items=sknEnum)
    SKL_FILES = EnumProperty(name='Skeleton Files', 
            description='Available Skeleton Files', items=sklEnum)
    TEX_FILES = EnumProperty(name='Texture Files', 
            description='Available Texture Files', items=texEnum)

    def updateFiles(self, directory):
        #print(self.sklEnum, self.sknEnum, self.texEnum)
        dirContents = listdir(directory)
        self.sklEnum = []
        self.sknEnum = []
        self.texEnum = []
        for file in dirContents:
            name, ext = path.splitext(file)
            if ext.lower() == '.skn':
                self.sknEnum.append((file,file,file))
            elif ext.lower() == '.skl':
                self.sklEnum.append((file,file,file))
            elif ext.lower() == '.dds':
                self.texEnum.append((file,file,file))
        self.DIRECTORY = directory
        bpy.props.RemoveProperty('SKN_FILES')
        SKN_FILES = EnumProperty(name='Model Files', 
            description='Available Model Files', items=sknEnum)


        
    def draw(self, context):
        layout = self.layout
        fileParams = bpy.context.space_data.params
        if fileParams.directory != self.DIRECTORY:
            print('Old:  %s\nNew:  %s' %(self.DIRECTORY,fileParams.directory))
            self.updateFiles(fileParams.directory)

        box = layout.box()
        box.prop(self.properties, 'DIRECTORY')
        box.prop(self.properties, 'SKN_FILES')
        box.prop(self.properties, 'SKL_FILES')
        box.prop(self.properties, 'TEX_FILES')

        #box.operator('BUTTONS_OT_file_browse')
        

    def invoke(self, context, event):
        print(event.type, event.value)

        wm = bpy.context.window_manager
        wm.add_fileselect(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        return {'FINISHED'}


def menu_func_import(self,context):
    self.layout.operator(ImportLoL_popup_dialog.bl_idname, text='LoL Data')

def register():
    bpy.types.INFO_MT_file_import.append(menu_func_import)

def unregister():
    bpy.types.INFO_MT_file_import.remove(menu_func_import)


if __name__ == '__main__':
    register()


def import_char(MODEL_DIR="", SKN_FILE=None, SKL_FILE=None, DDS_FILE=None):


    if SKL_FILE:
        SKL_FILEPATH=path.join(MODEL_DIR, SKL_FILE)
        sklHeader, boneDict = lolSkeleton.importSKL(SKL_FILEPATH)
        lolSkeleton.buildSKL(boneDict)
        armObj = bpy.data.objects['Armature']
        armObj.name ='lolArmature'

    if SKN_FILE:
        SKN_FILEPATH=path.join(MODEL_DIR, SKN_FILE)
        sknHeader, materials, indices, vertices = lolMesh.importSKN(SKN_FILEPATH)
        lolMesh.buildMesh(SKN_FILEPATH)
        meshObj = bpy.data.objects['Mesh']
        meshObj.name = 'lolMesh'
        
    if SKN_FILE and SKL_FILE:
        lolMesh.addDefaultWeights(boneDict, vertices, armObj, meshObj)

    if DDS_FILE:
        DDS_FILEPATH=path.join(MODEL_DIR, DDS_FILE)

        bpy.ops.object.mode_set(mode='EDIT')
        img = bpy.data.images.new(DDS_FILE)
        tex = bpy.data.textures.new('lolTexture', type='IMAGE')
        mat = bpy.data.materials.new('lolMaterial')

        img.filepath=DDS_FILEPATH
        img.source = 'FILE'

        meshObj.material_slots[0].material = mat
        mat.texture_slots.create(0)
        mat.texture_slots[0].texture = tex
        mat.texture_slots[0].texture_coords = 'UV'
        tex.image = img

        meshObj.data.uv_textures[0].data[0].image = img
        meshObj.data.uv_textures[0].data[0].use_image = True
        meshObj.data.uv_textures[0].data[0].blend_type = 'ALPHA'
