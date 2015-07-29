# ##### BEGIN GPL LICENSE BLOCK ##### #
# lolblender - Python addon to use League of Legends files into blender
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of  MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

import bpy
from bpy import props
from bpy_extras.io_utils import ImportHelper, ExportHelper
from . import lolMesh, lolSkeleton, lolAnimation
from os import path

__bpydoc__="""
Import/Export a League of Legends character model, including
skeleton and textures.
"""

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

class IMPORT_OT_lolanm(bpy.types.Operator, ImportHelper):
    bl_label="Import LoL Animation"
    bl_idname="import.lolanm"

    ANM_FILE = props.StringProperty(name='Animation', description='Animation .anm file')
    MODEL_DIR = props.StringProperty()
       
    def draw(self, context):
        layout = self.layout
        fileProps = context.space_data.params
        self.MODEL_DIR = fileProps.directory
        
        selectedFileExt = path.splitext(fileProps.filename)[-1].lower()
        if selectedFileExt == '.anm':
            self.ANM_FILE = fileProps.filename
        box = layout.box()
        box.prop(self.properties, 'ANM_FILE')
        
    def execute(self, context):
        import_animation(MODEL_DIR=self.MODEL_DIR,
                    ANM_FILE=self.ANM_FILE)
               
        return {'FINISHED'}

class EXPORT_OT_lol(bpy.types.Operator, ExportHelper):
    '''Export a mesh as a League of Legends .skn file'''

    bl_idname="export.lol"
    bl_label = "Export .skn"

    VERSION = props.IntProperty(name='Version No.', description='.SKN version number', default=4)
    OUTPUT_FILE = props.StringProperty(name='Export File', description='File to which model will be exported')
    BASE_ON_IMPORT = props.BoolProperty(name='Base On Imported SKN', description='Base writing on an imported SKN of choice', default=True)
    INPUT_FILE = props.StringProperty(name='Import File', description='File to import certain metadata from')
    MODEL_DIR = props.StringProperty()

    filename_ext = '.skn'
    def draw(self, context):
        layout = self.layout
        fileProps = context.space_data.params
        self.MODEL_DIR = fileProps.directory

        selectedFileExt = path.splitext(fileProps.filename)[-1].lower()
        
        self.OUTPUT_FILE = fileProps.filename

        box = layout.box()
        box.prop(self.properties, 'VERSION')
        box.prop(self.properties, 'OUTPUT_FILE')
        box.prop(self.properties, 'BASE_ON_IMPORT')
        box.prop(self.properties, 'INPUT_FILE')
        
    def execute(self, context):
        export_char(MODEL_DIR=self.MODEL_DIR,
                OUTPUT_FILE=self.OUTPUT_FILE,
                INPUT_FILE=self.INPUT_FILE,
                BASE_ON_IMPORT=self.BASE_ON_IMPORT,
                VERSION=self.VERSION)

        return {'FINISHED'}
        
class IMPORT_OT_sco(bpy.types.Operator, ImportHelper):
    '''Import a League of Legends .sco file'''

    bl_idname="import.sco"
    bl_label="Import .sco"

    filename_ext = '.sco'

    def execute(self, context):
        import_sco(self.properties.filepath)
        return {'FINISHED'}
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

    if CLEAR_SCENE:
        for type in ['MESH', 'ARMATURE', 'LATTICE', 'CURVE', 'SURFACE']:
            bpy.ops.object.select_by_type(extend=False, type=type)
            bpy.ops.object.delete()

    if SKL_FILE:
        SKL_FILEPATH=path.join(MODEL_DIR, SKL_FILE)
        #sklHeader, boneDict = lolSkeleton.importSKL(SKL_FILEPATH)
        sklHeader, boneList, reorderedBoneList = lolSkeleton.importSKL(SKL_FILEPATH)
        lolSkeleton.buildSKL(boneList, sklHeader.version)
        armObj = bpy.data.objects['Armature']
        armObj.name ='lolArmature'
        armObj.data.draw_type = 'STICK'
        armObj.data.show_axes = True
        armObj.show_x_ray = True

    if SKN_FILE:
        SKN_FILEPATH=path.join(MODEL_DIR, SKN_FILE)
        sknHeader, materials, metaData, indices, vertices = lolMesh.importSKN(SKN_FILEPATH)
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
        if reorderedBoneList == []:
           lolMesh.addDefaultWeights(boneList, vertices, armObj, meshObj)
        else:
           print('Using reordered Bone List')
           lolMesh.addDefaultWeights(reorderedBoneList, vertices, armObj, meshObj)

    if DDS_FILE and APPLY_TEXTURE:
        DDS_FILEPATH=path.join(MODEL_DIR, DDS_FILE)
        try:  # in case user is already in object mode (ie, SKN and DDS but no SKL)
            bpy.ops.object.mode_set(mode='OBJECT')
        except RuntimeError:
            pass
        bpy.ops.object.select_all(action='DESELECT')

        img = bpy.data.images.load(DDS_FILEPATH)
        img.source = 'FILE'

        img_name = DDS_FILE[:-4]  # remove .dds
        tex = bpy.data.textures.new(img_name + '_texImage', type='IMAGE')
        tex.image = img
        mat = bpy.data.materials.new(name=(img_name + '_mat'))
        mat.use_shadeless = True

        mtex = mat.texture_slots.add()
        mtex.texture = tex
        mtex.texture_coords = 'UV'
        mtex.use_map_color_diffuse = True

        meshObj.data.materials.append(mat)

def import_animation(MODEL_DIR="", ANM_FILE=""):
    '''Import an Animation for a LoL character
    MODEL_DIR:  Base directory of the animation you wish to import.
    ANM_FILE:  .anm animation file
    '''

    if ANM_FILE:
        ANM_FILEPATH=path.join(MODEL_DIR, ANM_FILE)

    animationHeader, boneList = lolAnimation.importANM(ANM_FILEPATH)
    lolAnimation.applyANM(animationHeader, boneList)
    

def export_char(MODEL_DIR='',
                OUTPUT_FILE='untitled.skn',
                INPUT_FILE='',
                BASE_ON_IMPORT=False,
                VERSION=2):
    '''Exports a mesh as a LoL .skn file.

    MODEL_DIR:      Base directory of the input and output file.
    OUTPUT_FILE:    Name of the file that will be created.
    INPUT_FILE:     Name of the file from which certain meta-data will be taken
    BASE_ON_IMPORT: Indicator on whether to take metadata from INPUT_FILE
    VERSION:        Version of the SKN we will be making
    '''
    import bpy

    print("model_dir:%s" % MODEL_DIR)
    

    #If no mesh object was supplied, try the active selection
    if bpy.context.object.type =='MESH':
        meshObj = bpy.context.object
    #If the selected object wasn't a mesh, try finding one named 'lolMesh'
    else:
        try:
            meshObj = bpy.data.objects['lolMesh']
        except KeyError:
            errStr = '''
            No mesh selected, and no mesh
            named 'lolMesh'.  Nothing to export.'''
            print(errStr)
            raise KeyError

    input_filepath = path.join(MODEL_DIR, INPUT_FILE)
    output_filepath = path.join(MODEL_DIR, OUTPUT_FILE)

    # Z values of the SKL and such are inverted, but the SKN isn't. This was
    # left over from previous export trials, probably
    # bpy.ops.transform.resize(value=(1,1,-1), constraint_axis=(False, False,
    #         True), constraint_orientation='GLOBAL')
    lolMesh.exportSKN(meshObj, output_filepath, input_filepath, BASE_ON_IMPORT, VERSION)
    # bpy.ops.transform.resize(value=(1,1,-1), constraint_axis=(False, False,
    #         True), constraint_orientation='GLOBAL')

def import_sco(filepath):
    import lolMesh
    lolMesh.buildSCO(filepath)

def menu_func_import(self, context):
    self.layout.operator(IMPORT_OT_lol.bl_idname, text='League of Legends Character (.skn;.skl)')
    # self.layout.operator(IMPORT_OT_lolanm.bl_idname, text='League of Legends Animation(.anm)')
    # self.layout.operator(IMPORT_OT_sco.bl_idname, text='League of Legends Particle (.sco)')


def menu_func_export(self, context):
    self.layout.operator(EXPORT_OT_lol.bl_idname, text="League of Legends (.skn)")

def register():
    bpy.utils.register_class(IMPORT_OT_lol)
    bpy.utils.register_class(IMPORT_OT_lolanm)
    bpy.utils.register_class(IMPORT_OT_sco)
    bpy.types.INFO_MT_file_import.append(menu_func_import)

    bpy.utils.register_class(EXPORT_OT_lol)
    bpy.types.INFO_MT_file_export.append(menu_func_export)

def unregister():
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)









def test_anm():
    base_dir = "C:\\Users\\Tath\\Downloads\\New folder\\DATA\\Characters\\Annie\\"
    skn = "Annie.skn"
    skl = "Annie.skl"
    anm_dir = base_dir + "animations\\"
    anm = "annie_channel.anm"

    skn_path = base_dir + skn
    skl_path = base_dir + skl
    anm_path = anm_dir + anm

    skl_header, skl_bone_list, reordered_bone_list = lolSkeleton.importSKL(skl_path)
    anm_header, anm_bone_list = lolAnimation.importANM(anm_path)

    import_char(MODEL_DIR=base_dir, SKN_FILE=skn, SKL_FILE=skl, DDS_FILE="",
            CLEAR_SCENE=True, APPLY_WEIGHTS=True, APPLY_TEXTURE=False)
    import_animation(MODEL_DIR=anm_dir, ANM_FILE=anm)

    boneCheckList = ['r_hand']
    for bone in skl_bone_list:
        print("SKL bone: %r" % bone.name)
        if bone.name.lower() in boneCheckList:
            print("p: %s" % bone.matrix[3::4])
    for bone in anm_bone_list:
        if bone.name.lower() in boneCheckList:
            print("ANM bone: %s" % bone.name)
            for f in range(0, anm_header.numFrames):
                print("p: %s" % bone.get_frame(f)[0])

