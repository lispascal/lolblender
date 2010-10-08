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
    'name': 'Import a League of Legends Skeleton file (.skl)',
    'author': 'Zac Berkowitz',
    'version': '0.2',
    'blender': (2,5,3),
    'location': 'File > Import',
    'category': 'Import/Export',
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
        #Presently io_scene_obj.load() does not import vertex normals, 
        #so do it ourselves
        for id, vtx in enumerate(meshObj.data.vertices):
            vtx.normal = vertices[id]['normal']
        
    if SKN_FILE and SKL_FILE and APPLY_WEIGHTS:
        lolMesh.addDefaultWeights(boneDict, vertices, armObj, meshObj)

    if DDS_FILE and APPLY_TEXTURE:
        DDS_FILEPATH=path.join(MODEL_DIR, DDS_FILE)
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects['lolMesh'].select = True
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
        meshObj.data.update()
        bpy.ops.object.mode_set(mode='OBJECT')
