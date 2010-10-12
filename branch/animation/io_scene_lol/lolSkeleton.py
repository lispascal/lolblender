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
from collections import UserDict
import struct

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
        self['name'] = bytes.decode(fields[0])
        self['parent'], self['scale'] = fields[1:3]
        
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
    from mathutils import Matrix

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
        #boneAlignToAxis = (0,1,0)


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
            #newBone.head = arm.edit_bones[boneParentName].tail
            newBone.use_hinge = False
            newBone.use_inherit_scale = False


        newBone.align_roll(boneAlignToAxis)
        newBone.lock = False
        #newBone.use_local_location = False

        '''
        #Edit the 4x4 transformation matrix directly.  Matrix
        #is stored in column major order:
        #
        # [3x3 rotation matrix | 3x1 translation: tail location  ]
        # [--------------------|-------------------------------- ]
        # [1x3 0's             | 1x1 'scale' scalar (1.0)        ]
        tMatrix = [ [0.0]*4, [0.0]*4, [0.0]*4, [0.0]*4 ]

        #3x3 rotation
        #tMatrix[0][:3] = [bone['matrix'][0][0], bone['matrix'][1][0],
            #bone['matrix'][2][0]]
        #tMatrix[1][:3] = [bone['matrix'][0][1], bone['matrix'][1][1],
            #bone['matrix'][2][1]]
        #tMatrix[2][:3] = [bone['matrix'][0][0], bone['matrix'][1][0],
            #bone['matrix'][2][0]]
        tMatrix[0][:3] = [bone['matrix'][0][0], bone['matrix'][0][1],
            bone['matrix'][0][2]]
        tMatrix[1][:3] = [bone['matrix'][1][0], bone['matrix'][1][1],
            bone['matrix'][1][2]]
        tMatrix[2][:3] = [bone['matrix'][2][0], bone['matrix'][2][1],
            bone['matrix'][2][2]]

        #3x1 tail location
        tMatrix[0][3] = bone['matrix'][0][3]
        tMatrix[1][3] = bone['matrix'][1][3]
        tMatrix[2][3] = bone['matrix'][2][3]

        #1x1 scalar
        tMatrix[3][3] = 1

        #Set as bone transform
        newBone.transform(Matrix(tMatrix[0], tMatrix[1], tMatrix[2], tMatrix[3]))
        #newBone.tail = boneTail
        #print(boneName) 
        #print(tMatrix[0])
        #print(tMatrix[1])
        #print(tMatrix[2])
        #print(tMatrix[3])
        #print(Matrix(tMatrix[0],tMatrix[1],tMatrix[2],tMatrix[3]))
        #If this is a root bone set the y offset to 0 for the head element
        if boneParentID == -1:
            newBone.head[:] = (boneTail[0],0,boneTail[2])
            newBone.tail = boneTail

        if boneParentID > -1:
            boneParentName = boneDict[boneParentID]['name']
            newBone.parent = arm.edit_bones[boneParentName]
            newBone.use_connect = True

            parentBone = arm.bones[boneParentName]
            parentTail = parentBone.tail
            newBone.length = (Vector(boneTail)-parentTail).magnitude
            #newBone.head = arm.edit_bones[boneParentName].tail
            #newBone.use_hinge = True 
            newBone.use_inherit_scale = False


        #newBone.align_roll(boneAlignToAxis)
        newBone.lock = False
        #newBone.use_local_location = False
    '''    
    bpy.ops.object.mode_set(mode='OBJECT')


