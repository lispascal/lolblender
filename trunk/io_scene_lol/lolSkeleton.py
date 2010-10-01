import UserDict
import struct
#import bpy
#from bpy.props import *
#from io_utils import ImportHelper


class sklHeader(UserDict):
    """LoL skeleton header format:
    fileType        char[8]     8       version string
    numObjects      int         4       number of objects (skeletons)
    skeletonHash    int         4       unique id number?
    numElements     int         4       number of bones

    total size                  20 Bytes
    """

    def __init__(self):
        UserDict.__init__(self)
        self.__format__ = '<8s3i'
        self.__size__ = struct.calcsize(self.__format__)
        self['fileType'] = None
        self['numObjects'] = None
        self['skeletonHash'] = None
        self['numElements'] = None

    def fromFile(self, sklFile):
        """Reads the skl header object from the raw binary file"""
        sklFile.seek(0)
        fields = struct.unpack(self.__format__, sklFile.read(self.__size__))
        (fileType, self['numObjects'], 
                self['skeletonHash'], self['numElements']) = fields

        self['fileType'] = bytes.decode(fileType)
        #self.fileType = fileType

    
    def toFile(self, sklFile):
        """Writes the header object to a raw binary file"""
        data = struct.pack(self.__format__, self['fileType'], self['numObjects'],
                self['skeletonHash'], self['numElements'])
        sklFile.write(data)


class sklBone(UserDict):
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
        UserDict.__init__(self)
        self.__format__ = '<32sif12f'
        self.__size__ = struct.calcsize(self.__format__)
        self['name'] = None
        self['parent'] = None
        self['scale'] = None
        self['matrix'] = [[],[],[]]


    def fromFile(self,sklFile):
        """Reads skeleton bone object from a binary file fid"""

        fields = struct.unpack(self.__format__, sklFile.read(self.__size__))
        self.name = bytes.decode(fields[0])
        self.parent, self.scale = fields[1:3]
        
        #Strip null \x00's from the name

        self['matrix'][0] = list( fields[3:7] )
        self['matrix'][1] = list( fields[7:11] )
        self['matrix'][2] = list( fields[11:15] )

    def toFile(self,sklFile):
        """Writes skeleton bone object to a binary file FID"""

        data = struct.pack('<32sif', self['name'], self['parent'], self['scale'])
        for j in range(3):
            for k in range(4):
                data += struct.pack('<f', self['matrix'][j][k]) 

        sklFile.write(data)

def importSKL(filepath):
    header = sklHeader()
    boneDict = {}
    #Wrap open in try block
    sklFid = open(filepath, 'rb')

    #Read the file header to get # of bones
    header.fromFile(sklFid)

    #Read in the bones
    for k in range(header['numElements']):
        boneDict[k] = sklBone()
        boneDict[k].fromFile(sklFid)

    sklFid.close()
    return header, boneDict


def buildSKL(boneDict):
    import bpy
    #Create Blender Armature
    bpy.ops.object.armature_add(location=(0,0,0), enter_editmode=True)
    obj = bpy.context.active_object
    arm = obj.data

    bones = arm.edit_bones
    #Remove the default bone
    bones.remove(bones[0])

    #import the bones
    for boneID, bone in boneDict.items():
        boneName = bone['name']
        boneTail = (bone['matrix'][0][3], bone['matrix'][1][3], bone['matrix'][2][3])
        boneParentID = bone['parent']

        boneAlignToAxis= (bone['matrix'][0][2], bone['matrix'][1][2],
                bone['matrix'][2][2])


        newBone = arm.edit_bones.new(boneName)
        newBone.tail[:] = boneTail
        
        #If this is a root bone set the y offset to 0 for the head element
        if boneParentID == -1:
            newBone.head[:] = (boneTail[0],0,boneTail[2])

        #If this bone is a child, find the parent's tail and attach this bone's
        #head to it
        if boneParentID > -1:
            boneParentName = boneDict[boneParentID]['name']
            newBone.parent = arm.edit_bones[boneParentName]
            newBone.use_connect = True


        newBone.align_roll(boneAlignToAxis)
        newBone.lock = True

    bpy.ops.object.mode_set(mode='OBJECT')


