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
import mathutils

class sklHeader():
    """LoL skeleton header format:
v1-2
    fileType        char[8]     8       id string
    version      int            4       possibly number of objects (1-2), 0 is different version
    skeletonHash    int         4       unique id number?
    numBones        int         4       number of bones

    total size                  20 Bytes

v0
    fileType        char[8]     8       id string
    version         int         4       version # (0)
    zero            short       2       ?
    numBones        short       2       
    numBoneIDs      int         4
    offsetVertexData    short   2       usually 64
    unknown         short       2       if 0, maybe this and above are one int

    offset1         int         4       ?
    offsetToAnimationIndices    4       
    offset2         int         4       ?
    offset3         int         4       ?
    offsetToStrings int         4    
    empty                       20

    total size                  64 Bytes          

    """

    def __init__(self):
        self.__format__i = '<8si'
        self.__format__v12 = '<2i'
        self.__format__v0 = '<2hi2h5i'
        self.__size__i = struct.calcsize(self.__format__i)
        self.__size__v12 = struct.calcsize(self.__format__v12)
        self.__size__v0 = struct.calcsize(self.__format__v0)
        self.fileType = None
        self.version = None
        self.skeletonHash = None
        self.numBones = None

    def fromFile(self, sklFile):
        """Reads the skl header object from the raw binary file"""
        sklFile.seek(0)
        beginning = struct.unpack(self.__format__i, sklFile.read(self.__size__i))
        (fileType, self.version) = beginning
        if self.version in [1, 2]:  # 1 or 2
            rest = struct.unpack(self.__format__v12, sklFile.read(self.__size__v12))
            (self.skeletonHash, self.numBones) = rest
        elif self.version == 0:  # version 0
            rest = struct.unpack(self.__format__v0, sklFile.read(self.__size__v0))
            (self.zero, self.numBones, self.numBoneIDs, self.offsetVertexData,
                    self.unknown, self.offset1, self.offsetAnimationIndices,
                    self.offset2, self.offset3, self.offsetToStrings) = rest
            sklFile.seek(self.offsetVertexData)
        # fields = struct.unpack(self.__format__, sklFile.read(self.__size__))
        # (fileType, self.version, 
        #         self.skeletonHash, self.numBones) = fields

        # self.fileType = bytes.decode(fileType)
        self.fileType = fileType

    
    def toFile(self, sklFile):
        """Writes the header object to a raw binary file"""
        data = struct.pack(self.__format__, self.fileType, self.version,
                self.skeletonHash, self.numBones)
        sklFile.write(data)


class sklBone():
    """LoL Bone structure format
    v1-2
    name        char[32]    32      name of bone
    parent      int         4       id # of parent bone. Root bone = -1
    scale       float       4       scale
    matrix      float[3][4] 48      affine bone matrix
                                    [x1 x2 x3 xt
                                     y1 y2 y3 yt
                                     z1 z2 z3 zt]
    total                   88
    
    v0  (thanks to LolViewer makers)
    zero        short       2       ?
    id          short       2       
    parent      short       2       
    unknown     short       2       ? combined with above gives int?
    "namehash"  int         4       
    twopointone float       4       the value 2.1 as a float. 
                                    maybe a scaling, 2.1 value for most .skls
    position    float[3]    12      position of bone
    scaling?    float[3]    12      possibly scaling in x-y-z. values of 1
    orientation float[4]    16      quaternion of orientation
    ct          float[3]    12      "ctx, cty, ctz", probably another position
                                    ("translation")
    padding?    byte[32]    32      

    total                   100
    """
    def __init__(self):
        self.__format__v12 = '<32sif12f'
        self.__size__v12 = struct.calcsize(self.__format__v12)
        self.__format__v0 = '<4hi14f'
        self.__size__v0 = struct.calcsize(self.__format__v0)
        self.name = None
        self.parent = None
        self.scale = None
        self.matrix = [[],[],[]]


    def fromFile(self,sklFile, version):
        """Reads skeleton bone object from a binary file fid"""
        if version in [1,2]:
            fields = struct.unpack(self.__format__v12, 
                    sklFile.read(self.__size__v12))
            self.name = bytes.decode(fields[0])
            self.parent, self.scale = fields[1:3]
            #Strip null \x00's from the name

            self.matrix[0] = list( fields[3:7] )
            self.matrix[1] = list( fields[7:11] )
            self.matrix[2] = list( fields[11:15] )

            #Flip z axis
            for k in range(4):
                self.matrix[2][k] = -self.matrix[2][k]
        elif version == 0:
            fields = struct.unpack(self.__format__v0,
                    sklFile.read(self.__size__v0))
            self.id = fields[1]
            self.parent = fields[2]
            self.name = fields[4]
            twopointone = fields[5]
            self.position = list(fields[6:9])
            self.position[2] *= 1
            self.scale = fields[9:12]
            self.quat = mathutils.Quaternion([
                    - fields[15], fields[12], fields[13],
                    -fields[14]])
            self.matrix = self.quat.to_matrix()
            self.matrix2 = [[],[],[],[]]
            for i in range(0,3):
                self.matrix2[i] = [self.matrix[i][0], self.matrix[i][1], 
                        self.matrix[i][2], self.position[0]]
            self.matrix2[3] = [0, 0, 0, 1]
            # print(self.matrix)
            self.ct = list(fields[16:19])
            # print("q%s" % self.quat)
            # print("m%s" % self.matrix)
            # print("p%s" % self.position)
            # print("c%s" % self.ct)
            sklFile.seek(sklFile.tell()+32)  # skip 32 padding bytes

        else:
            raise ValueError('unhandled version number', version)

    def toFile(self,sklFile):
        """Writes skeleton bone object to a binary file FID"""

        data = struct.pack('<32sif', self.name, self.parent, self.scale)
        for j in range(3):
            for k in range(4):
                data += struct.pack('<f', self.matrix[j][k]) 

        sklFile.write(data)

    def copy(self):
        newBone = sklBone()
        newBone.name = self.name
        newBone.parent = self.parent
        newBone.scale = self.scale
        newBone.matrix = self.matrix
        try:
            newBone.quat = self.quat
        except:
            pass
        return newBone


def importSKL(filepath):
    header = sklHeader()
    boneList= []
    reorderedBoneList = []
    
    #Wrap open in try block
    sklFid = open(filepath, 'rb')

    #Read the file header to get # of bones
    header.fromFile(sklFid)
    if header.version in [1, 2]:
        #Read in the bones
        for k in range(header.numBones):
            boneList.append(sklBone())
            boneList[k].fromFile(sklFid, header.version)
        


        if header.version == 2:  # version 2 has a reordered bone list
            #Read in reordered bone assignments
            numBoneIDs = struct.unpack('<i', sklFid.read(4))[0]  # clue taken from LolViewer
            for i in range(0, numBoneIDs):
                buf = sklFid.read(4)
                if buf == b'':
                    break
                else:
                    boneId = struct.unpack('<i', buf)[0]

                print(buf,boneId)
                reorderedBoneList.append(boneList[boneId].copy())
            print(len(reorderedBoneList))
    elif header.version == 0:
        # taken from c# code from LoLViewer
        for k in range(header.numBones):
            boneList.append(sklBone())
            boneList[k].fromFile(sklFid, header.version)
        sklFid.seek(header.offset1)
        # indices for version 4 animation
        header.boneIDMap = {}
        for i in range(0, header.numBones):
            # 8 bytes
            sklID, anmID = struct.unpack('<2i', sklFid.read(
                    struct.calcsize('<2i')))
            header.boneIDMap[anmID] = sklID



        sklFid.seek(header.offsetToStrings)
        for i in range(0, header.numBones):
            name = []
            while name.count(b'\0') == 0:
                for j in range(0,4):
                    name.append(sklFid.read(1))
            end = name.index(b'\0')
            boneList[i].name = ''.join(
                    v.decode() for v in name[0:end]).lower()

        # below is technically earlier in file than above
        sklFid.seek(header.offsetAnimationIndices)
        for i in range(0, header.numBoneIDs):
            boneId = struct.unpack('<h', sklFid.read(
                    struct.calcsize('<h')))[0]
            reorderedBoneList.append(boneList[boneId].copy())



    sklFid.close()
    return header, boneList, reorderedBoneList


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

def buildSKL(boneList, version):
    import bpy
    #Create Blender Armature
    bpy.ops.object.armature_add(location=(0,0,0), enter_editmode=True)
    obj = bpy.context.active_object
    arm = obj.data

    bones = arm.edit_bones
    #Remove the default bone
    # bones.remove(bones[0])
    #import the bones
    if version in [1,2]:
        for boneID, bone in enumerate(boneList):
            boneName = bone.name.rstrip('\x00')
            try:
                boneHead = (bone.matrix[0][3], bone.matrix[1][3], bone.matrix[2][3])
            except:
                print(bone.matrix)
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
    elif version == 0:
        for boneID, bone in enumerate(boneList):
            #If this bone is a child, find the parent's tail and attach this bone's
            #head to it
            boneHead = mathutils.Vector([0,0,0])
            parentTail = mathutils.Vector([0,0,0])
            boneTail = mathutils.Vector(bone.position)
            boneParentID = bone.parent
            boneName = bone.name.rstrip('\x00')
            # debug
            # if boneName.count("uparm"):
            #     print("%s, id:%s\nc%s\np:%s\nq:%s\ns:%s" % (bone.name, boneID, bone.ct, bone.position, bone.quat, bone.scale))

            newBone = arm.edit_bones.new(boneName)
            if boneParentID > -1:
                boneParentName = boneList[boneParentID].name
                parentBone = arm.edit_bones[boneParentName]

                newBone.parent = parentBone
                # bone.quat = boneList[boneParentID].quat * bone.quat
                parentTail = parentBone.tail
                #build chains of successively parented bones
                if boneParentID == (boneID - 1):
                    # parentBone.tail = newBone.head
                    newBone.use_connect = True 

            
            #If this is a root bone set the y offset to 0 for the head element
            #if boneParentID == -1:
            #    newBone.head[:] = (boneHead[0],0,boneHead[2])
            newBone.head = parentTail + boneHead
            # boneTail.rotate(bone.quat)
            newBone.tail = parentTail + boneTail




        #Final loop through bones.  Find bones w/out children & align to parent (for
        #now

        # for bone in arm.edit_bones:
        #     if len(bone.children) == 0:
        #         bone.length = 10
        #         #If the orphan bone has a parent
        #         if bone.parent:
        #             bone.align_orientation(bone.parent)


    bpy.ops.object.mode_set(mode='OBJECT')


