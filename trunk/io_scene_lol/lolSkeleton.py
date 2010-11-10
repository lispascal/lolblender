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
import struct

class sklHeader():
    """LoL skeleton header format:
    fileType        char[8]     8       version string
    numObjects      int         4       number of objects (skeletons)
    skeletonHash    int         4       unique id number?
    numElements     int         4       number of bones

    total size                  20 Bytes
    """

    def __init__(self):
        self.__format__ = '<8s3i'
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


class sklBone():
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

        #Flip z axis
        for k in range(4):
            self.matrix[2][k] = -self.matrix[2][k]

    def toFile(self,sklFile):
        """Writes skeleton bone object to a binary file FID"""

        data = struct.pack('<32sif', self.name, self.parent, self.scale)
        for j in range(3):
            for k in range(4):
                data += struct.pack('<f', self.matrix[j][k]) 

        sklFile.write(data)

def importSKL(filepath):
    header = sklHeader()
    boneList= []
    #Wrap open in try block
    sklFid = open(filepath, 'rb')

    #Read the file header to get # of bones
    header.fromFile(sklFid)

    #Read in the bones
    for k in range(header.numElements):
        boneList.append(sklBone())
        boneList[k].fromFile(sklFid)

    sklFid.close()
    return header, boneList


def buildSKL2(filename):
    import bpy
    from mathutils import Matrix, Vector
    from math import acos, sqrt

    header, boneList = importSKL(filename)
    #Create Blender Armature
    bpy.ops.object.armature_add(location=(0,0,0), enter_editmode=True)
    obj = bpy.context.active_object
    arm = obj.data

    bones = arm.edit_bones
    #Remove the default bone
    bones.remove(bones[0])

    #import the bones
    M = Matrix()
    V = Vector()
    boneDict = {}
    for boneID, bone in enumerate(boneList):

        boneName = (bone.name).rstrip('\x00')
        boneDict[boneName] = boneID
        boneHead = (bone.matrix[0][3], bone.matrix[1][3], bone.matrix[2][3])
        boneParentID = bone.parent
        

        boneAlignToAxis= (bone.matrix[0][2], bone.matrix[1][2],
                bone.matrix[2][2])

        #M[0][:3] = bone.matrix[0][:3]
        #M[1][:3] = bone.matrix[1][:3]
        #M[2][:3] = bone.matrix[2][:3]

        #V[:3] = boneHead
        newBone = arm.edit_bones.new(boneName)
        newBone.head = boneHead
        
        #If this is a root bone set the y offset to 0 for the head element
        #if boneParentID == -1:
            #newBone.head[:] = (boneTail[0],0,boneTail[2])

        #If this bone is a child, find the parent's tail and attach this bone's
        #head to it
        if boneParentID > -1:
            boneParentName = boneList[boneParentID].name
            parentBone = arm.edit_bones[boneParentName]
            newBone.parent = parentBone

            #Bone chains run sequentially to the end, if the parent
            #id = current id -1, move the parent's tail to the child's head
            if boneParentID+1 == boneID:
                parentBone.tail = newBone.head
                #newBone.use_connect = True

            #Don't yet know what to do here
            else:
                pass
                #newBone.length = 1.0/bone.scale
                
            #newBone.parent = arm.edit_bones[boneParentName]
            #newBone.use_connect = True

    #Catch bones with no children
    #print(boneDict)
    sqrt3 = sqrt(3)
    for bone in arm.edit_bones:
        if len(bone.children) == 0:
            print(bone.name)
            boneId = boneDict[bone.name]
            boneMatrix = boneList[boneId].matrix
            length = 1.0/boneList[boneId].scale
            #bone.length = length
            
            
            #bone.align_orientation(bone.parent)
            #get the bone normal, it's the
            # -x basis vector after rotating
            x = Vector((boneMatrix[0][0], boneMatrix[1][0], boneMatrix[2][0]))
            x = -x
            y = Vector((boneMatrix[0][1], boneMatrix[1][1], boneMatrix[2][1]))
            z = Vector((boneMatrix[0][2], boneMatrix[1][2], boneMatrix[2][2]))
            #M[0][:3] = boneMatrix[0]
            #M[1][:3] = boneMatrix[1]
            #M[2][:3] = boneMatrix[2]
            #M[3] = [0,0,0,1]
            bone.tail = bone.head
            bone.tail += length*x
            '''
            bone.tail = bone.head + x*length
            theta = bone.x_axis.dot(y)
            print('bone_x:', bone.x_axis, '\ndesired:', y)
            print('x_theta:', theta)
            if abs(theta) > 1:
                pass

            elif theta > 0.95:
                pass

            else:
                theta = acos(theta)
                bone.roll += theta


            theta = bone.z_axis.dot(z)
            print('bone_z:', bone.z_axis, '\ndesired:', z)
            print('z_theta:', theta)
            if abs(theta) > 1:
                pass
            elif theta > 0.95:
                pass
            else:
                theta = acos(theta)
                Mr = Matrix.Rotation(theta, 4, bone.x_axis)

                v = bone.tail-bone.head
                v = Mr*v
                bone.tail = bone.head + v
                     

            #bone.length=1.0/bone.scale
            y_axis = x
            x_axis = y

            z_axis = x_axis.cross(y_axis)
            bone.align_roll(z)
            #theta = z_axis.dot(z)
            #Mr = Matrix.Rotation(3.14159, 4, x_axis)
            #print(theta)
            #z_axis = -z_axis
            #bone.tail = length*(x_axis+y_axis+z_axis)/sqrt(3.0)+bone.head

            #Another kind
            #x_vec = Vector((length, 0, 0))
            #m = Matrix((boneMatrix[0][0], boneMatrix[1][0], boneMatrix[2][0]),
            #            (boneMatrix[0][1], boneMatrix[1][1], boneMatrix[2][1]),
            #            (boneMatrix[0][2], boneMatrix[1][2], boneMatrix[2][2]))

            '''
            #print(bone.name, length, boneNormal)
        #newBone.align_roll(boneAlignToAxis)
        #newBone.lock = True
    bpy.ops.object.mode_set(mode='OBJECT')

def buildSKL(boneList):
    import bpy
    #Create Blender Armature
    bpy.ops.object.armature_add(location=(0,0,0), enter_editmode=True)
    obj = bpy.context.active_object
    arm = obj.data

    bones = arm.edit_bones
    #Remove the default bone
    bones.remove(bones[0])
    #import the bones
    for boneID, bone in enumerate(boneList):
        boneName = bone.name.rstrip('\x00')
        boneHead = (bone.matrix[0][3], bone.matrix[1][3], bone.matrix[2][3])
        boneParentID = bone.parent

        boneAlignToAxis= (bone.matrix[0][2], bone.matrix[1][2],
                bone.matrix[2][2])


        newBone = arm.edit_bones.new(boneName)
        #newBone.head[:] = boneTail
        
        #If this is a root bone set the y offset to 0 for the head element
        #if boneParentID == -1:
        #    newBone.head[:] = (boneHead[0],0,boneHead[2])
        newBone.head = boneHead

        #If this bone is a child, find the parent's tail and attach this bone's
        #head to it
        if boneParentID > -1:
            boneParentName = boneList[boneParentID].name
            parentBone = arm.edit_bones[boneParentName]
            newBone.parent = parentBone
            #build chains of successively parented bones
            if boneParentID == (boneID - 1):
                parentBone.tail = newBone.head
                newBone.use_connect = True


    #Final loop through bones.  Find bones w/out children & align to parent (for
    #now

    for bone in arm.edit_bones:
        if len(bone.children) == 0:
            bone.length = 10
            #If the orphan bone has a parent
            if bone.parent:
                bone.align_orientation(bone.parent)


    bpy.ops.object.mode_set(mode='OBJECT')


