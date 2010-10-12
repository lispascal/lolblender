import lolMesh, lolSkeleton
import bpy

def run():
    dataBase = '/var/tmp/downloads/lol/DATA/Characters/'
    sknFile = 'Ryze/Ryze.skn'
    sklFile = 'Ryze/Ryze.skl'

    sklHeader, boneDict = lolSkeleton.importSKL(dataBase + sklFile)
    lolSkeleton.buildSKL(boneDict)

    sknHeader, materials, indices, vertices = lolMesh.importSKN(dataBase + sknFile)
    lolMesh.buildMesh(dataBase + sknFile)

    meshObj = bpy.data.objects['Mesh']
    armObj = bpy.data.objects['Armature']

    lolMesh.addDefaultWeights(boneDict, vertices, armObj, meshObj)
