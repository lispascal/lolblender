import struct
import bpy
from bpy.props import *
from io_utils import ImportHelper
import sys

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

class importSKL(bpy.types.Operator, ImportHelper):
    bl_idname = 'import_scene.lol_skl'
    bl_label = 'Import SKL'

    filename_ext = '.skl'
    filter_glob = StringProperty(default='*.skl', options={'HIDDEN'})

    def execute(self, context):
        #print('Selected: ' + context.active_object.name)
        import_skl(self.filepath)
        return{'FINISHED'}

class sklHeader(object):
    """LoL skeleton header format:
    fileType        char[8]     8       version string
    numObjects      int         4       number of objects (skeletons)
    skeletonHash    int         4       unique id number?
    numElements     int         4       number of bones

    total size                  20 Bytes
    """
    __format__ = '<8s3i'

    def __init__(self):
        self.__size__ = struct.calcsize(self.__format__)
        self.fileType = None
        self.numObjects = None
        self.skeletonHash = None
        self.numElements = None

    def fromFile(self, sklFile):
        """Reads the skl header object from the raw binary file"""
        sklFile.seek(0)
        fields = struct.unpack(self.__format__, sklFile.read(self.__size__))
        (fileType, self.numObjects, 
                self.skeletonHash, self.numElements) = fields

        self.fileType = bytes.decode(fileType)
        #self.fileType = fileType

    
    def toFile(self, sklFile):
        """Writes the header object to a raw binary file"""
        data = struct.pack(self.__format__, self.fileType, self.numObjects,
                self.skeletonHash, self.numElements)
        sklFile.write(data)


class sklBone(object):
    """LoL Bone structure format
    name        char[32]    32      name of bone
    parent      int         4       id # of parent bone. Root bone = -1
    scale       float       4       scale
    matrix      float[3][4] 48      affine bone matrix
                                    [x1 x2 x3 xt
                                     y1 y2 y3 yt
                                     z1 z2 z3 zt]

    total                   88
    """



    def __init__(self):
        self.__format__ = '<32sif12f'
        self.__size__ = struct.calcsize(self.__format__)
        self.name = None
        self.parent = None
        self.scale = None
        self.matrix = [[],[],[]]


    def fromFile(self,sklFile):
        """Reads skeleton bone object from a binary file fid"""

        fields = struct.unpack(self.__format__, sklFile.read(self.__size__))
        self.name = bytes.decode(fields[0])
        self.parent, self.scale = fields[1:3]
        
        #Strip null \x00's from the name

        self.matrix[0] = list( fields[3:7] )
        self.matrix[1] = list( fields[7:11] )
        self.matrix[2] = list( fields[11:15] )

    def toFile(self,sklFile):
        """Writes skeleton bone object to a binary file FID"""

        data = struct.pack('<32sif', self.name, self.parent, self.scale)
        for j in range(3):
            for k in range(4):
                data += struct.pack('<f', self.matrix[j][k]) 

        sklFile.write(data)


def import_skl(sklFilename):
    header = sklHeader()
    boneDict = {}
    #Wrap open in try block
    print(sklFilename, sys.stderr)
    sklFid = open(sklFilename, 'rb')

    #Read the file header to get # of bones
    header.fromFile(sklFid)

    #Read in the bones
    for k in range(header.numElements):
        boneDict[k] = sklBone()
        boneDict[k].fromFile(sklFid)

    #Create Blender Armature
    bpy.ops.object.armature_add(location=(0,0,0), enter_editmode=True)
    obj = bpy.context.active_object
    arm = obj.data

    bones = arm.edit_bones
    #Remove the default bone
    bones.remove(bones[0])

    #import the bones
    for boneID, bone in boneDict.items():
        boneName = bone.name
        boneTail = (bone.matrix[0][3], bone.matrix[1][3], bone.matrix[2][3])
        boneParentID = bone.parent

        boneAlignToAxis= (bone.matrix[0][2], bone.matrix[1][2],
                bone.matrix[2][2])


        newBone = arm.edit_bones.new(boneName)
        newBone.tail[:] = boneTail
        
        #If this is the root bone, make a 0 length bone?, no
        if boneParentID == -1:
            newBone.head[:] = (0,0,0)

        if boneParentID > -1:
            boneParentName = boneDict[boneParentID].name
            newBone.parent = arm.edit_bones[boneParentName]
            newBone.use_connect = True


        newBone.align_roll(boneAlignToAxis)
        newBone.lock = True

    bpy.ops.object.mode_set(mode='OBJECT')

def menu_func_import(self,context):
    self.layout.operator(importSKL.bl_idname, text='LoL SKeleton (.skl)')

def register():
    bpy.types.INFO_MT_file_import.append(menu_func_import)

def unregister():
    bpy.types.INFO_MT_file_import.remove(menu_func_import)


if __name__ == '__main__':
    register()
