# ##### BEGIN GPL LICENSE BLOCK ##### #
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>
__all__ = ['lolMesh', 'lolSkeleton']

bl_addon_info = {
    'name': 'Import League of Legends Character files (.skn;.skl)',
    'author': 'Zac Berkowitz',
    'version': (0,4),
    'blender': (2,5,3),
    'location': 'File > Import',
    'category': 'Import/Export',
    'api': 31878,
    'wiki_url': 'http://code.google.com/p/lolblender',
    'tracker_url':'http://code.google.com/p/lolblender/issues/list'
    }

__bpydoc__="""
Import/Export a League of Legends character model, including
skeleton and textures.
"""
def import_char(MODEL_DIR="", SKN_FILE="", SKL_FILE="", DDS_FILE="",
        CLEAR_SCENE=True, APPLY_WEIGHTS=True, APPLY_TEXTURE=True):
    '''Import a LoL Character
    MODEL_DIR:  Base directory of the model you wish to import.
    SKN_FILE:  .skn mesh file for the character
    SKL_FILE:  .skl skeleton file for the character
    DDS_FILE:  .dds texture file for the character
    CLEAR_SCENE: remove existing meshes, armatures, surfaces, etc.
                 before importing
    APPLY_WEIGHTS:  Import bone weights from the mesh file
    APPLY_TEXTURE:  Apply the skin texture

    !!IMPORTANT!!:
    If you're running this on a windows system make sure
    to escape the backslashes in the model directory you give.

    BAD:  c:\\path\\to\\model
    GOOD: c:\\\\path\\\\to\\\\model
    '''
    import bpy
    import lolMesh, lolSkeleton
    from os import path

    if CLEAR_SCENE:
        for type in ['MESH', 'ARMATURE', 'LATTICE', 'CURVE', 'SURFACE']:
            bpy.ops.object.select_by_type(extend=False, type=type)
            bpy.ops.object.delete()

    if SKL_FILE:
        SKL_FILEPATH=path.join(MODEL_DIR, SKL_FILE)
        #sklHeader, boneDict = lolSkeleton.importSKL(SKL_FILEPATH)
        sklHeader, boneList = lolSkeleton.importSKL(SKL_FILEPATH)
        lolSkeleton.buildSKL(boneList)
        armObj = bpy.data.objects['Armature']
        armObj.name ='lolArmature'
        armObj.data.draw_type = 'STICK'
        armObj.data.show_axes = True
        armObj.show_x_ray = True

    if SKN_FILE:
        SKN_FILEPATH=path.join(MODEL_DIR, SKN_FILE)
        sknHeader, materials, indices, vertices = lolMesh.importSKN(SKN_FILEPATH)
        lolMesh.buildMesh(SKN_FILEPATH)
        meshObj = bpy.data.objects['lolMesh']
        bpy.ops.object.select_all(action='DESELECT')
        meshObj.select = True
        bpy.ops.transform.resize(value=(1,1,-1), constraint_axis=(False, False,
            True), constraint_orientation='GLOBAL')
        #meshObj.name = 'lolMesh'
        #Presently io_scene_obj.load() does not import vertex normals, 
        #so do it ourselves
        #for id, vtx in enumerate(meshObj.data.vertices):
        #    vtx.normal = vertices[id]['normal']
        
    if SKN_FILE and SKL_FILE and APPLY_WEIGHTS:
        lolMesh.addDefaultWeights(boneList, vertices, armObj, meshObj)

    if DDS_FILE and APPLY_TEXTURE:
        DDS_FILEPATH=path.join(MODEL_DIR, DDS_FILE)
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        #bpy.data.objects['lolMesh'].select = True
        #bpy.ops.object.mode_set(mode='EDIT')

        img = bpy.data.images.new(DDS_FILE)
        img.filepath=DDS_FILEPATH
        img.source = 'FILE'

        tex = bpy.data.textures.new('lolTexture', type='IMAGE')
        tex.image = img
        mat = bpy.data.materials.new(name=tex.name)


        mtex = mat.texture_slots.add()
        mtex.texture = tex
        mtex.texture_coords = 'UV'
        mtex.use_map_color_diffuse = True

        meshObj.data.materials.append(mat)

        meshObj.data.uv_textures[0].data[0].image = img
        meshObj.data.uv_textures[0].data[0].use_image = True
        meshObj.data.uv_textures[0].data[0].blend_type = 'ALPHA'


def export_char(outputFile, meshObj = None):
    '''Exports a mesh as a LoL .skn file.

    outputFile:  Name of file to save the mesh as
    meshObj:  Blender mesh object to export.  If
        none is given we will look for one named
        'lolMesh'
    '''
    import bpy

    if meshObj == None:
        #If no mesh object was supplied, try the active selection
        if bpy.context.object.type =='MESH':
            meshObj = bpy.context.object
        #If the selected object wasn't a mesh, try finding one named 'lolMesh'
        else:
            try:
                meshObj = bpy.data.objects['lolMesh']
            except KeyError:
                errStr = '''
                No mesh object supplied, no mesh selected, and no mesh
named 'lolMesh'.  Nothing to export.'''
                print(errStr)
                raise KeyError

    bpy.ops.transform.resize(value=(1,1,-1), constraint_axis=(False, False,
            True), constraint_orientation='GLOBAL')
    lolMesh.exportSKN(meshObj, outputFile)
    bpy.ops.transform.resize(value=(1,1,-1), constraint_axis=(False, False,
            True), constraint_orientation='GLOBAL')

def import_sco(filepath):
    import lolMesh
    lolMesh.buildSCO(filepath)


import bpy
from bpy import props
from io_utils import ImportHelper, ExportHelper

from os import path

class IMPORT_OT_lol(bpy.types.Operator, ImportHelper):
    bl_label="Import LoL"
    bl_idname="import.lol"

    SKN_FILE = props.StringProperty(name='Mesh', description='Model .skn file')
    SKL_FILE = props.StringProperty(name='Skeleton', description='Model .skl file')
    DDS_FILE = props.StringProperty(name='Texture', description='Model .dds file')    
    MODEL_DIR = props.StringProperty()
    CLEAR_SCENE = props.BoolProperty(name='ClearScene', description='Clear current scene before importing?', default=True)
    APPLY_WEIGHTS = props.BoolProperty(name='LoadWeights', description='Load default bone weights from .skn file', default=True)
    
       
    def draw(self, context):
        layout = self.layout
        fileProps = context.space_data.params
        self.MODEL_DIR = fileProps.directory
        
        selectedFileExt = path.splitext(fileProps.filename)[-1].lower()
        if selectedFileExt == '.skn':
            self.SKN_FILE = fileProps.filename
        elif selectedFileExt == '.skl':
            self.SKL_FILE = fileProps.filename
        elif selectedFileExt == '.dds':
            self.DDS_FILE = fileProps.filename
        box = layout.box()
        box.prop(self.properties, 'SKN_FILE')
        box.prop(self.properties, 'SKL_FILE')
        box.prop(self.properties, 'DDS_FILE')
        box.prop(self.properties, 'CLEAR_SCENE', text='Clear scene before importing')
        box.prop(self.properties, 'APPLY_WEIGHTS', text='Load mesh weights')
        
    def execute(self, context):
        
        import_char(MODEL_DIR=self.MODEL_DIR,
                    SKN_FILE=self.SKN_FILE,
                    SKL_FILE=self.SKL_FILE,
                    DDS_FILE=self.DDS_FILE,
                    CLEAR_SCENE=self.CLEAR_SCENE,
                    APPLY_WEIGHTS=self.APPLY_WEIGHTS)
               
        return {'FINISHED'}

class EXPORT_OT_lol(bpy.types.Operator, ExportHelper):
    '''Export a mesh as a League of Legends .skn file'''

    bl_idname="export.lol"
    bl_label = "Export .skn"

    filename_ext = '.skn'

    def execute(self, context):
        export_char(self.properties.filepath)
        return {'FINISHED'}
        
class IMPORT_OT_sco(bpy.types.Operator, ImportHelper):
    '''Import a League of Legends .sco file'''

    bl_idname="import.sco"
    bl_label="Import .sco"

    filename_ext = '.sco'

    def execute(self, context):
        import_sco(self.filepath)
        return {'FINISHED'}



def menu_func_import(self, context):
    self.layout.operator(IMPORT_OT_lol.bl_idname, text='League of Legends Character (.skn;.skl)')
    self.layout.operator(IMPORT_OT_sco.bl_idname, text='League of Legends Particle (.sco)')


def menu_func_export(self, context):
    self.layout.operator(EXPORT_OT_lol.bl_idname, text="League of Legends (.skn)")

def register():
    bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.types.INFO_MT_file_export.append(menu_func_export)

def unregister():
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()
