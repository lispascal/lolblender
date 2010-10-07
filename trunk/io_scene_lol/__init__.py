__all__ = ['lolMesh', 'lolSkeleton']


def import_char(MODEL_DIR="", SKN_FILE="", SKL_FILE="", DDS_FILE="",
        APPLY_WEIGHTS=True, APPLY_TEXTURE=True):
    '''Import a LoL Character

    MODEL_DIR:  Base directory of the model you wish to import.
    SKN_FILE:  .skn mesh file for the character
    SKL_FILE:  .skl skeleton file for the character
    DDS_FILE:  .dds texture file for the character
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
        bpy.ops.object.mode_set(mode='OBJECT')
